"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { apiBase, apiHealthy } from "@/lib/api";
import {
  DEMO_CONCEPTS,
  DEMO_PERSONAS,
  DEMO_REPORT,
  DEMO_SCORECARD,
  DEMO_STUDY,
  type ConceptRow,
  type PersonaCard,
  type ReportRow,
  type Scorecard,
  type StudySummary,
} from "@/lib/demo-data";
import { fadeUp, stagger } from "@/lib/motion";

export default function StudioPage() {
  const [mode, setMode] = useState<"checking" | "live" | "demo">("checking");
  const [personas, setPersonas] = useState<PersonaCard[]>([]);
  const [study, setStudy] = useState<StudySummary | null>(null);
  const [report, setReport] = useState<ReportRow | null>(null);
  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [concepts, setConcepts] = useState<ConceptRow[]>(DEMO_CONCEPTS);
  const [selectedConcept, setSelectedConcept] = useState<string>(DEMO_CONCEPTS[0]?.path || "data/concepts/fintech_survey.json");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [visible, setVisible] = useState(0);

  useEffect(() => {
    (async () => {
      const healthy = await apiHealthy();
      if (!healthy) {
        setMode("demo");
        setPersonas(DEMO_PERSONAS);
        setStudy(DEMO_STUDY);
        setReport(DEMO_REPORT);
        setScorecard(DEMO_SCORECARD);
        setConcepts(DEMO_CONCEPTS);
        return;
      }
      setMode("live");
      setPersonas(DEMO_PERSONAS);
    })();
  }, []);

  useEffect(() => {
    if (!personas.length) return;
    setVisible(0);
    const id = setInterval(() => {
      setVisible((v) => {
        if (v >= personas.length) {
          clearInterval(id);
          return v;
        }
        return v + 1;
      });
    }, 120);
    return () => clearInterval(id);
  }, [personas]);

  async function runDemoFlow() {
    setBusy(true);
    setError(null);
    try {
      if (mode !== "live") {
        setPersonas(DEMO_PERSONAS);
        setStudy(DEMO_STUDY);
        setReport(DEMO_REPORT);
        setScorecard(DEMO_SCORECARD);
        setConcepts(DEMO_CONCEPTS);
        return;
      }
      const panelRes = await fetch(`${apiBase()}/panels?size=40&seed=42`, { method: "POST" });
      if (!panelRes.ok) throw new Error(`panels ${panelRes.status}`);
      const studyRes = await fetch(
        `${apiBase()}/studies?spec_path=${encodeURIComponent(selectedConcept)}&seed=42`,
        { method: "POST" },
      );
      if (!studyRes.ok) throw new Error(`studies ${studyRes.status}`);
      const studyJson = (await studyRes.json()) as StudySummary;
      setStudy(studyJson);
      const reportRes = await fetch(`${apiBase()}/reports/${studyJson.report_id}`);
      if (reportRes.ok) setReport(await reportRes.json());
      setPersonas(DEMO_PERSONAS);
    } catch (e) {
      setError(String(e));
      setMode("demo");
      setPersonas(DEMO_PERSONAS);
      setStudy(DEMO_STUDY);
      setReport(DEMO_REPORT);
      setScorecard(DEMO_SCORECARD);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-6 py-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl text-white">Research studio</h1>
          <p className="mt-1 text-xs uppercase tracking-wide text-zinc-500">
            {mode === "checking" && "Checking API..."}
            {mode === "live" && "Connected to FastAPI backend"}
            {mode === "demo" && "Showcase mode (API offline)"}
          </p>
        </div>
        <button
          disabled={busy}
          onClick={runDemoFlow}
          className="rounded-full bg-accent px-5 py-2 text-sm font-medium text-white shadow-accent disabled:opacity-50"
        >
          {busy ? "Running..." : "Run Pulse Budget survey"}
        </button>
      </div>
      {error && <p className="text-sm text-red-400">{error}</p>}


      <section className="rounded-2xl border border-white/[0.06] bg-ink-surface p-5">
        <h2 className="mb-3 font-display text-xl text-white">Bundled concepts</h2>
        <div className="flex flex-wrap gap-2">
          {concepts.map((c) => {
            const active = selectedConcept === c.path;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => setSelectedConcept(c.path)}
                className={`rounded-full border px-3 py-1 text-xs transition ${
                  active
                    ? "border-accent bg-accent/20 text-white"
                    : "border-white/[0.06] text-zinc-300 hover:border-accent/40"
                }`}
              >
                {c.title} · {c.type}
              </button>
            );
          })}
        </div>
      </section>

      <section className="rounded-2xl border border-white/[0.06] bg-ink-surface p-5">
        <h2 className="mb-4 font-display text-xl text-white">Panel assembling</h2>
        <motion.div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3" variants={stagger} initial="hidden" animate="show">
          {personas.slice(0, visible).map((p) => (
            <motion.div
              key={p.id}
              variants={fadeUp}
              className="rounded-2xl border border-white/[0.06] bg-ink-elevated p-4"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm text-accent">{p.id}</span>
                <span className="text-xs text-zinc-500">{p.tech_segment}</span>
              </div>
              <div className="mt-2 text-sm text-white">
                Age {p.age} · {p.region}
              </div>
              <div className="mt-1 text-xs text-zinc-500">
                {p.occupation} · {p.income_bin}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-white/[0.06] bg-ink-surface p-5">
          <h2 className="font-display text-xl text-white">Study metrics</h2>
          {!study && <p className="mt-3 text-sm text-zinc-500">Run a study to populate metrics.</p>}
          {study && (
            <div className="mt-4 grid grid-cols-2 gap-3">
              {[
                ["n", String(study.n)],
                ["attention", study.attention_pass_rate.toFixed(2)],
                ["consistency", study.consistency_rate.toFixed(2)],
                ["cost USD", study.cost_usd.toFixed(3)],
              ].map(([k, v]) => (
                <div key={k} className="rounded-2xl border border-white/[0.06] bg-ink-elevated p-4">
                  <div className="text-xs uppercase text-zinc-500">{k}</div>
                  <div className="mt-1 font-mono text-xl text-accent">{v}</div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-white/[0.06] bg-ink-surface p-5">
          <h2 className="font-display text-xl text-white">Pew scorecard snapshot</h2>
          {!scorecard && (
            <p className="mt-3 text-sm text-zinc-500">
              Showcase includes a scorecard sample. Live runs: `make validate`.
            </p>
          )}
          {scorecard && (
            <div className="mt-4 space-y-3">
              <div className="font-mono text-accent">
                MAE {scorecard.mean_mae} · directional {scorecard.directional_agreement_rate}
              </div>
              {scorecard.questions.slice(0, 4).map((q) => (
                <div key={q.question_id} className="rounded-xl border border-white/[0.06] p-3 text-sm">
                  <div className="flex justify-between gap-2">
                    <span className="text-zinc-300">{q.question_id}</span>
                    <span className={q.directional_agreement ? "text-emerald-400" : "text-amber-400"}>
                      {q.directional_agreement ? "agree" : "diverge"}
                    </span>
                  </div>
                  <div className="mt-1 text-xs text-zinc-500">
                    truth {q.truth_top} · synth {q.synth_top} · mae {q.mae}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <section className="rounded-2xl border border-white/[0.06] bg-ink-surface p-5">
        <h2 className="font-display text-xl text-white">Research report</h2>
        {!report && <p className="mt-3 text-sm text-zinc-500">No report yet.</p>}
        {report && (
          <div className="mt-4 space-y-4">
            <p className="text-sm leading-relaxed text-zinc-300">{report.summary}</p>
            <div className="text-xs uppercase tracking-wide text-zinc-500">
              verification {report.verification_ok ? "ok" : "flagged"} · cost ${report.cost_usd}
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {report.insights.map((ins) => (
                <div key={ins.segment} className="rounded-2xl border border-white/[0.06] bg-ink-elevated p-4">
                  <div className="font-mono text-xs text-accent">{ins.segment}</div>
                  <p className="mt-2 text-sm text-zinc-300">{ins.text}</p>
                  <div className="mt-2 text-xs text-zinc-500">count {ins.count}</div>
                </div>
              ))}
            </div>
            {report.objections.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {report.objections.map((o) => (
                  <span
                    key={o.theme}
                    className="rounded-full border border-white/[0.06] px-3 py-1 text-xs text-zinc-300"
                  >
                    {o.theme}: {o.count}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
