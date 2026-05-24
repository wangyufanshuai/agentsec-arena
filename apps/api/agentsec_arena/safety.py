from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlparse

from .models import SafetyDecision


CLOUD_METADATA_HOSTS = {
    "169.254.169.254",
    "metadata.google.internal",
    "metadata",
}

FORBIDDEN_COMMAND_FRAGMENTS = {
    "--network host",
    "/var/run/docker.sock",
    "\\\\.\\pipe\\docker_engine",
    "docker.sock",
}


@dataclass(frozen=True)
class ToolGateway:
    allowlist_hosts: set[str]
    allow_localhost_ports: set[int]
    docker_subnets: tuple[str, ...] = ("172.16.0.0/12", "10.0.0.0/8")

    def validate_target(self, target: str) -> SafetyDecision:
        lowered = target.strip().lower()
        for fragment in FORBIDDEN_COMMAND_FRAGMENTS:
            if fragment in lowered:
                return SafetyDecision(
                    allowed=False,
                    reason=f"forbidden command fragment: {fragment}",
                    normalized_target=target,
                    violation_level="high",
                )

        parsed = urlparse(target if "://" in target else f"http://{target}")
        host = (parsed.hostname or target).strip("[]").lower()
        port = parsed.port

        if host in CLOUD_METADATA_HOSTS:
            return SafetyDecision(
                allowed=False,
                reason="cloud metadata targets are always denied",
                normalized_target=host,
                violation_level="high",
            )

        if host in {"localhost", "127.0.0.1", "::1"}:
            if port in self.allow_localhost_ports:
                return SafetyDecision(
                    allowed=True,
                    reason="mapped localhost target port is registered for this run",
                    normalized_target=host,
                )
            return SafetyDecision(
                allowed=False,
                reason="localhost port is not registered for this run",
                normalized_target=host,
                violation_level="high",
            )

        if host in self.allowlist_hosts:
            return SafetyDecision(
                allowed=True,
                reason="target service is in the current run allowlist",
                normalized_target=host,
            )

        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            return SafetyDecision(
                allowed=False,
                reason="domain is not a registered local scenario service",
                normalized_target=host,
                violation_level="high",
            )

        if ip.is_loopback:
            return SafetyDecision(
                allowed=False,
                reason="loopback IP requires an explicitly registered mapped port",
                normalized_target=host,
                violation_level="high",
            )

        if ip.is_link_local or ip.is_global:
            return SafetyDecision(
                allowed=False,
                reason="public or link-local target is outside the local range",
                normalized_target=host,
                violation_level="high",
            )

        for subnet in self.docker_subnets:
            if ip in ipaddress.ip_network(subnet):
                return SafetyDecision(
                    allowed=True,
                    reason="target IP is within the configured Docker lab subnet",
                    normalized_target=host,
                )

        return SafetyDecision(
            allowed=False,
            reason="private IP is not in the configured Docker lab subnet",
            normalized_target=host,
            violation_level="high",
        )

