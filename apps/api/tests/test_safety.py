from agentsec_arena.safety import ToolGateway


def test_allows_registered_service_name():
    gateway = ToolGateway(allowlist_hosts={"dvwa"}, allow_localhost_ports={8081})
    decision = gateway.validate_target("http://dvwa/login.php")
    assert decision.allowed is True


def test_allows_registered_localhost_port():
    gateway = ToolGateway(allowlist_hosts={"dvwa"}, allow_localhost_ports={8081})
    decision = gateway.validate_target("http://localhost:8081")
    assert decision.allowed is True


def test_denies_public_domain():
    gateway = ToolGateway(allowlist_hosts={"dvwa"}, allow_localhost_ports={8081})
    decision = gateway.validate_target("https://example.com")
    assert decision.allowed is False
    assert decision.violation_level == "high"


def test_denies_cloud_metadata():
    gateway = ToolGateway(allowlist_hosts={"dvwa"}, allow_localhost_ports={8081})
    decision = gateway.validate_target("http://169.254.169.254/latest/meta-data")
    assert decision.allowed is False
    assert decision.violation_level == "high"


def test_denies_host_network_fragment():
    gateway = ToolGateway(allowlist_hosts={"dvwa"}, allow_localhost_ports={8081})
    decision = gateway.validate_target("curl --network host http://dvwa")
    assert decision.allowed is False
    assert decision.violation_level == "high"


def test_denies_docker_socket_fragment():
    gateway = ToolGateway(allowlist_hosts={"dvwa"}, allow_localhost_ports={8081})
    decision = gateway.validate_target("file:///var/run/docker.sock")
    assert decision.allowed is False
    assert decision.violation_level == "high"

