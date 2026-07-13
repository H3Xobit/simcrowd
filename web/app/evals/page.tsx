"use client";

import { useEffect, useState } from "react";
import { DEMO_EVAL } from "@/lib/demo-data";

type EvalRow = typeof DEMO_EVAL;

export default function EvalsPage() {
  const [data, setData] = useState<EvalRow>(DEMO_EVAL);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
    fetch(`${base}/evals/latest.json`, { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => {
        if (j) setData(j);
      })
      .catch(() => undefined);
  }, []);

  const rows = [
    ["Panel max marginal error", data.panel_max_marginal_error, "<= 0.03"],
    ["Consistency rate", data.consistency_rate, ">= 0.90"],
    ["Attention pass rate", data.attention_pass_rate, "report"],
    ["Report verification", data.report_verification_ok ? 1 : 0, "1"],
    ["Reproducible", data.reproducible ? 1 : 0, "1"],
    ["Pew mean MAE", data.pew_mean_mae, "honest"],
    ["Pew directional agree", data.pew_directional_agreement_rate, "honest"],
    ["Cost / study USD", data.cost_per_study_usd, "< 1.00"],
  ] as const;

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="font-display text-3xl text-white md:text-5xl">Validation and evals</h1>
      <p className="mt-3 max-w-2xl text-zinc-400">
        Public metrics from the offline harness. Divergence vs Pew is part of the product story, not hidden.
      </p>
      <div className="mt-8 overflow-hidden rounded-2xl border border-white/[0.06]">
        <table className="w-full text-left text-sm">
          <thead className="bg-ink-surface text-zinc-500">
            <tr>
              <th className="px-4 py-3 font-medium">Metric</th>
              <th className="px-4 py-3 font-medium">Value</th>
              <th className="px-4 py-3 font-medium">Gate / note</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([k, v, note]) => (
              <tr key={k} className="border-t border-white/[0.06]">
                <td className="px-4 py-3 text-zinc-300">{k}</td>
                <td className="px-4 py-3 font-mono text-accent">
                  {typeof v === "number" ? v : String(v)}
                </td>
                <td className="px-4 py-3 text-zinc-500">{note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-4 text-xs text-zinc-600">
        Snapshot {data.timestamp} · n={data.n} · latency {data.latency_s}s
      </p>
    </main>
  );
}
