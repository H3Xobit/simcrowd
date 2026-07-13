"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";
import { fadeUp, stagger } from "@/lib/motion";

const features = [
  {
    title: "Joint-distribution panels",
    body: "Sample whole ACS person records with weights so age, income, education, and region stay jointly realistic.",
  },
  {
    title: "Surveys, interviews, concepts",
    body: "Run closed surveys, 5-turn laddering interviews, and concept tests against the same persona panel.",
  },
  {
    title: "Verified synthesis",
    body: "Segmented insights, objection maps, and Van Westendorp pricing with cited persona IDs and recomputed counts.",
  },
  {
    title: "Pew reality validation",
    body: "Replicate published topline questions on the synthetic panel and publish MAE, JS divergence, and directional agreement.",
  },
];

const stats = [
  { label: "Panel size", value: "200" },
  { label: "Cost / survey", value: "< $1" },
  { label: "Pew questions", value: "8+" },
  { label: "Consistency gate", value: "> 0.9" },
];

export default function LandingPage() {
  const reduce = useReducedMotion();
  return (
    <main>
      <section className="shader-hero relative overflow-hidden border-b border-white/[0.06]">
        <div className="pointer-events-none absolute inset-0 persona-field opacity-50" />
        <div className="pointer-events-none absolute inset-0 opacity-40">
          <div className="absolute -right-10 top-10 h-72 w-72 animate-pulse rounded-full bg-accent/20 blur-3xl" />
          <div className="absolute bottom-0 left-10 h-56 w-56 rounded-full bg-accent/10 blur-3xl" />
        </div>
        <motion.div
          className="relative mx-auto max-w-6xl px-6 py-24 md:py-32"
          variants={reduce ? undefined : stagger}
          initial={reduce ? undefined : "hidden"}
          animate={reduce ? undefined : "show"}
        >
          <motion.p variants={fadeUp} className="mb-4 text-sm uppercase tracking-[0.2em] text-accent">
            Synthetic user research
          </motion.p>
          <motion.h1
            variants={fadeUp}
            className="max-w-4xl font-display text-5xl leading-[1.05] tracking-tight text-white md:text-7xl"
          >
            SimCrowd
          </motion.h1>
          <motion.p variants={fadeUp} className="mt-6 max-w-2xl text-lg text-zinc-400">
            Build demographically grounded persona panels, run surveys and interviews in parallel,
            then prove where the synthetic sample tracks (and misses) real Pew toplines.
          </motion.p>
          <motion.div variants={fadeUp} className="mt-10 flex flex-wrap gap-3">
            <Link
              href="/app"
              className="rounded-full bg-accent px-6 py-3 text-sm font-medium text-white shadow-accent"
            >
              Open studio
            </Link>
            <Link
              href="/evals"
              className="rounded-full border border-white/[0.06] bg-ink-surface px-6 py-3 text-sm text-zinc-200"
            >
              Validation scorecard
            </Link>
          </motion.div>
          <motion.div variants={fadeUp} className="mt-16 grid grid-cols-2 gap-4 md:grid-cols-4">
            {stats.map((s) => (
              <div
                key={s.label}
                className="rounded-2xl border border-white/[0.06] bg-ink-surface/80 p-4"
              >
                <div className="font-mono text-2xl text-accent">{s.value}</div>
                <div className="mt-1 text-sm text-zinc-500">{s.label}</div>
              </div>
            ))}
          </motion.div>
        </motion.div>
      </section>

      <motion.section
        className="mx-auto max-w-6xl px-6 py-24 md:py-32"
        variants={stagger}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-80px" }}
      >
        <motion.h2 variants={fadeUp} className="font-display text-3xl text-white md:text-5xl">
          Rigorous synthetic research
        </motion.h2>
        <motion.p variants={fadeUp} className="mt-4 max-w-2xl text-zinc-400">
          The point is honesty: where panels agree with published surveys, and where they diverge.
        </motion.p>
        <div className="mt-12 grid gap-4 md:grid-cols-2">
          {features.map((f) => (
            <motion.div
              key={f.title}
              variants={fadeUp}
              className="rounded-2xl border border-white/[0.06] bg-ink-elevated p-6"
            >
              <h3 className="text-lg text-white">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">{f.body}</p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      <motion.section
        className="border-t border-white/[0.06] bg-ink-surface/40"
        variants={stagger}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-80px" }}
      >
        <div className="mx-auto max-w-6xl px-6 py-24 md:py-32">
          <motion.h2 variants={fadeUp} className="font-display text-3xl text-white md:text-5xl">
            Panel to report in one path
          </motion.h2>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {[
              { step: "01", title: "Sample", body: "Weighted ACS joint draw into 200 personas with seeded backstories." },
              { step: "02", title: "Research", body: "Fan-out surveys and laddering interviews with attention and consistency checks." },
              { step: "03", title: "Validate", body: "Score synthetic answers against Pew toplines; ship the scorecard with the report." },
            ].map((s) => (
              <motion.div key={s.step} variants={fadeUp} className="rounded-2xl border border-white/[0.06] p-6">
                <div className="font-mono text-accent">{s.step}</div>
                <h3 className="mt-3 text-xl text-white">{s.title}</h3>
                <p className="mt-2 text-sm text-zinc-400">{s.body}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>
    </main>
  );
}
