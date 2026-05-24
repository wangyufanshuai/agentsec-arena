"use client";

import {
  Activity,
  Bot,
  FileText,
  Gauge,
  Lock,
  Play,
  Radar,
  RefreshCw,
  Shield,
  Square,
  Terminal,
  TriangleAlert
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { api } from "@/lib/api";
import { demoRun, demoScenarios } from "@/lib/demo-data";
import type { Report, RunBundle, Scenario } from "@/lib/types";

const navItems = [
  { label: "Scenarios", icon: Radar },
  { label: "Runs", icon: Activity },
  { label: "Reports", icon: FileText },
  { label: "Settings", icon: Lock }
];

const attackTactics = ["Recon", "Initial Access", "Execution", "Defense Evasion", "Collection", "Impact"];

function cx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

function statusTone(status: string) {
  if (status === "completed" || status === "running" || status === "attacker_complete" || status === "defender_complete") {
    return "bg-teal/10 text-teal border-teal/20";
  }
  if (status === "safety_violation" || status === "failed") {
    return "bg-coral/10 text-coral border-coral/20";
  }
  return "bg-slate-100 text-slate-700 border-slate-200";
}

function severityTone(severity: string) {
  if (severity === "high" || severity === "critical") return "text-coral";
  if (severity === "medium") return "text-amber";
  return "text-teal";
}

function Panel({ children, className }: { children: React.ReactNode; className?: string }) {
  return <section className={cx("rounded-lg border border-line bg-panel shadow-panel", className)}>{children}</section>;
}

function PanelHeader({ title, icon: Icon, action }: { title: string; icon: LucideIcon; action?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-line px-4 py-3">
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4 text-teal" aria-hidden />
        <h2 className="text-sm font-semibold text-ink">{title}</h2>
      </div>
      {action}
    </div>
  );
}

function PrimaryButton({
  children,
  onClick,
  disabled,
  icon: Icon
}: {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  icon: LucideIcon;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="inline-flex h-9 items-center gap-2 rounded-md bg-ink px-3 text-sm font-semibold text-white transition hover:bg-black disabled:cursor-not-allowed disabled:opacity-45"
    >
      <Icon className="h-4 w-4" aria-hidden />
      {children}
    </button>
  );
}

function SecondaryButton({
  children,
  onClick,
  disabled,
  icon: Icon
}: {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  icon: LucideIcon;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="inline-flex h-9 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-semibold text-ink transition hover:border-teal/50 hover:text-teal disabled:cursor-not-allowed disabled:opacity-45"
    >
      <Icon className="h-4 w-4" aria-hidden />
      {children}
    </button>
  );
}

export function Dashboard() {
  const [scenarios, setScenarios] = useState<Scenario[]>(demoScenarios);
  const [selectedScenario, setSelectedScenario] = useState("dvwa");
  const [activeRun, setActiveRun] = useState<RunBundle>(demoRun);
  const [report, setReport] = useState<Report | null>(null);
  const [apiState, setApiState] = useState<"demo" | "connected" | "error">("demo");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    try {
      const [scenarioData, runData] = await Promise.all([api.scenarios(), api.runs()]);
      setScenarios(scenarioData);
      if (runData[0]) setActiveRun(runData[0]);
      setApiState("connected");
    } catch {
      setApiState("error");
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  const selected = useMemo(
    () => scenarios.find((scenario) => scenario.id === selectedScenario) ?? scenarios[0],
    [scenarios, selectedScenario]
  );

  async function guardedAction(action: () => Promise<RunBundle | Report>, updateRun = true) {
    setBusy(true);
    try {
      const result = await action();
      if (updateRun) setActiveRun(result as RunBundle);
      else setReport(result as Report);
      setApiState("connected");
    } catch {
      setApiState("error");
    } finally {
      setBusy(false);
    }
  }

  const score = activeRun.score ?? { attacker: 0, defender: 0, safety: 100, total: 30, rationale: [] };
  const latestEvents = [...activeRun.events].slice(-8).reverse();

  return (
    <main className="min-h-screen bg-canvas">
      <div className="grid min-h-screen grid-cols-1 md:grid-cols-[232px_1fr]">
        <aside className="border-b border-line bg-white px-4 py-5 md:border-b-0 md:border-r">
          <div className="mb-8 flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-lg bg-ink text-white">
              <Shield className="h-5 w-5" aria-hidden />
            </div>
            <div>
              <h1 className="text-lg font-bold leading-tight text-ink">AgentSec Arena</h1>
              <p className="text-xs font-medium text-muted">Local-only</p>
            </div>
          </div>
          <nav className="grid grid-cols-2 gap-1 md:block md:space-y-1">
            {navItems.map((item, index) => (
              <button
                key={item.label}
                className={cx(
                  "flex h-10 w-full items-center gap-3 rounded-md px-3 text-sm font-semibold",
                  index === 0 ? "bg-teal/10 text-teal" : "text-muted hover:bg-slate-50 hover:text-ink"
                )}
              >
                <item.icon className="h-4 w-4" aria-hidden />
                {item.label}
              </button>
            ))}
          </nav>
          <div className="mt-4 rounded-lg border border-teal/20 bg-teal/5 p-3 md:mt-8">
            <div className="mb-2 flex items-center gap-2 text-sm font-bold text-teal">
              <Lock className="h-4 w-4" aria-hidden />
              Safety Guard Active
            </div>
            <p className="text-xs leading-5 text-muted">
              Public domains, host networking, and Docker socket access are denied before tool execution.
            </p>
          </div>
        </aside>

        <section className="flex min-w-0 flex-col">
          <header className="flex min-h-16 flex-wrap items-center justify-between gap-3 border-b border-line bg-white px-4 py-3 md:px-6">
            <div>
              <p className="text-xs font-semibold uppercase text-muted">AI cyber range defense evaluation</p>
              <h2 className="text-xl font-bold text-ink">Arena Control Console</h2>
            </div>
            <div className="flex items-center gap-2">
              <span
                className={cx(
                  "rounded-md border px-2.5 py-1 text-xs font-bold",
                  apiState === "connected" ? "border-teal/20 bg-teal/10 text-teal" : "border-amber/20 bg-amber/10 text-amber"
                )}
              >
                {apiState === "connected" ? "API connected" : "Demo fallback"}
              </span>
              <SecondaryButton icon={RefreshCw} onClick={refresh} disabled={busy}>
                Refresh
              </SecondaryButton>
            </div>
          </header>

          <div className="grid flex-1 grid-cols-1 gap-5 p-4 xl:grid-cols-[minmax(0,1fr)_340px] xl:p-5">
            <div className="min-w-0 space-y-5">
              <Panel>
                <PanelHeader
                  title="Scenarios"
                  icon={Radar}
                  action={
                    <PrimaryButton
                      icon={Play}
                      disabled={busy || !selected}
                      onClick={() => selected && guardedAction(() => api.createRun(selected.id))}
                    >
                      Start Run
                    </PrimaryButton>
                  }
                />
                <div className="grid grid-cols-1 gap-3 p-4 lg:grid-cols-3">
                  {scenarios.map((scenario) => (
                    <button
                      key={scenario.id}
                      onClick={() => setSelectedScenario(scenario.id)}
                      className={cx(
                        "min-h-[150px] rounded-lg border p-4 text-left transition",
                        selectedScenario === scenario.id
                          ? "border-teal bg-teal/5"
                          : "border-line bg-white hover:border-teal/40"
                      )}
                    >
                      <div className="mb-3 flex items-start justify-between gap-3">
                        <div>
                          <h3 className="text-sm font-bold text-ink">{scenario.name}</h3>
                          <p className="mt-1 text-xs font-semibold uppercase text-muted">{scenario.type}</p>
                        </div>
                        <span className="rounded-md border border-line px-2 py-1 text-xs font-bold text-muted">
                          {scenario.service_name}
                        </span>
                      </div>
                      <p className="line-clamp-3 text-xs leading-5 text-muted">{scenario.description}</p>
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {scenario.tags.slice(0, 3).map((tag) => (
                          <span key={tag} className="rounded bg-slate-100 px-2 py-1 text-[11px] font-semibold text-slate-600">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </button>
                  ))}
                </div>
              </Panel>

              <Panel>
                <PanelHeader title="Active Run Timeline" icon={Activity} />
                <div className="grid gap-4 p-4 lg:grid-cols-[1.1fr_0.9fr]">
                  <div>
                    <div className="mb-3 flex flex-wrap items-center gap-2">
                      <span className={cx("rounded-md border px-2.5 py-1 text-xs font-bold", statusTone(activeRun.run.status))}>
                        {activeRun.run.status}
                      </span>
                      <span className="text-sm font-semibold text-muted">{activeRun.run.network_name}</span>
                      <span className="text-sm text-muted">{activeRun.run.mapped_target_url}</span>
                    </div>
                    <div className="space-y-3">
                      {activeRun.steps.length ? (
                        activeRun.steps.map((step) => (
                          <div key={step.id} className="rounded-lg border border-line bg-white p-3">
                            <div className="flex items-center justify-between gap-3">
                              <div className="flex items-center gap-2">
                                <Bot className={cx("h-4 w-4", step.agent === "attacker" ? "text-coral" : "text-teal")} aria-hidden />
                                <span className="text-sm font-bold text-ink">{step.agent}</span>
                                <span className="text-xs font-semibold text-muted">{step.action}</span>
                              </div>
                              <span className="text-xs font-bold text-muted">{step.status}</span>
                            </div>
                            <p className="mt-2 text-sm leading-5 text-muted">{step.output_summary}</p>
                            {step.tool_call ? (
                              <p className="mt-2 rounded bg-slate-50 px-2 py-1 font-mono text-xs text-slate-600">
                                {step.tool_call.tool} - {step.tool_call.target}
                              </p>
                            ) : null}
                          </div>
                        ))
                      ) : (
                        <p className="rounded-lg border border-dashed border-line p-4 text-sm text-muted">
                          No agent steps yet. Start attacker and defender agents for this run.
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="grid grid-cols-3 gap-2">
                      {activeRun.run.containers.map((container) => (
                        <div key={container.name} className="rounded-lg border border-line bg-white p-3">
                          <p className="truncate text-xs font-bold text-ink">{container.name}</p>
                          <p className="mt-1 text-[11px] font-semibold uppercase text-muted">{container.role}</p>
                          <p className="mt-2 text-xs font-bold text-teal">{container.status}</p>
                        </div>
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <SecondaryButton icon={Bot} disabled={busy} onClick={() => guardedAction(() => api.startAttacker(activeRun.run.id))}>
                        Start Attacker
                      </SecondaryButton>
                      <SecondaryButton icon={Shield} disabled={busy} onClick={() => guardedAction(() => api.startDefender(activeRun.run.id))}>
                        Start Defender
                      </SecondaryButton>
                      <SecondaryButton icon={Square} disabled={busy} onClick={() => guardedAction(() => api.stopRun(activeRun.run.id))}>
                        Stop
                      </SecondaryButton>
                    </div>
                  </div>
                </div>
              </Panel>

              <div className="grid gap-5 lg:grid-cols-[1fr_1fr]">
                <Panel>
                  <PanelHeader title="Findings" icon={TriangleAlert} />
                  <div className="overflow-auto p-4 thin-scrollbar">
                    <table className="w-full min-w-[560px] text-left">
                      <thead className="text-xs uppercase text-muted">
                        <tr>
                          <th className="pb-2">Finding</th>
                          <th className="pb-2">Severity</th>
                          <th className="pb-2">Mapping</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-line text-sm">
                        {activeRun.findings.map((finding) => (
                          <tr key={finding.id}>
                            <td className="py-3">
                              <p className="font-semibold text-ink">{finding.title}</p>
                              <p className="mt-1 text-xs text-muted">{finding.affected_target}</p>
                            </td>
                            <td className={cx("py-3 font-bold", severityTone(finding.severity))}>{finding.severity}</td>
                            <td className="py-3 text-xs text-muted">{[...finding.owasp, ...finding.cwe].slice(0, 2).join(", ")}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Panel>

                <Panel>
                  <PanelHeader title="ATT&CK Matrix" icon={Radar} />
                  <div className="grid grid-cols-2 gap-2 p-4 md:grid-cols-3">
                    {attackTactics.map((tactic) => {
                      const active = activeRun.findings.some((finding) => finding.attack.length > 0) && ["Recon", "Initial Access"].includes(tactic);
                      return (
                        <div
                          key={tactic}
                          className={cx(
                            "rounded-lg border p-3",
                            active ? "border-coral/30 bg-coral/10 text-coral" : "border-line bg-white text-muted"
                          )}
                        >
                          <p className="text-xs font-bold">{tactic}</p>
                        </div>
                      );
                    })}
                  </div>
                </Panel>
              </div>
            </div>

            <aside className="space-y-5">
              <Panel>
                <PanelHeader title="Score" icon={Gauge} />
                <div className="p-4">
                  <div className="grid place-items-center">
                    <div className="grid h-36 w-36 place-items-center rounded-full border-[12px] border-teal/20 bg-white">
                      <div className="text-center">
                        <p className="text-4xl font-black text-ink">{score.total}</p>
                        <p className="text-xs font-bold uppercase text-muted">total</p>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 space-y-3">
                    {[
                      ["Attacker", score.attacker, "bg-coral"],
                      ["Defender", score.defender, "bg-teal"],
                      ["Safety", score.safety, "bg-ink"]
                    ].map(([label, value, color]) => (
                      <div key={label as string}>
                        <div className="mb-1 flex justify-between text-xs font-bold text-muted">
                          <span>{label}</span>
                          <span>{value as number}</span>
                        </div>
                        <div className="h-2 rounded-full bg-slate-100">
                          <div className={cx("h-2 rounded-full", color as string)} style={{ width: `${value as number}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Panel>

              <Panel>
                <PanelHeader
                  title="Report"
                  icon={FileText}
                  action={
                    <SecondaryButton icon={FileText} disabled={busy} onClick={() => guardedAction(() => api.createReport(activeRun.run.id), false)}>
                      Generate
                    </SecondaryButton>
                  }
                />
                <div className="max-h-64 overflow-auto p-4 thin-scrollbar">
                  {report ? (
                    <pre className="whitespace-pre-wrap font-mono text-xs leading-5 text-muted">{report.content}</pre>
                  ) : (
                    <p className="text-sm leading-6 text-muted">
                      Generate Report creates a Markdown attack and defense summary with safety boundary, findings, timeline, score, and mitigation notes.
                    </p>
                  )}
                </div>
              </Panel>

              <Panel>
                <PanelHeader title="Live Logs" icon={Terminal} />
                <div className="max-h-[310px] space-y-2 overflow-auto p-4 thin-scrollbar">
                  {latestEvents.map((event) => (
                    <div key={event.id} className="rounded-md bg-slate-950 px-3 py-2 font-mono text-xs text-slate-100">
                      <span className={severityTone(event.severity)}>[{event.severity}]</span> {event.source}/{event.event_type}: {event.message}
                    </div>
                  ))}
                </div>
              </Panel>
            </aside>
          </div>
        </section>
      </div>
    </main>
  );
}
