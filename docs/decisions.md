# Decisions log

Format: `YYYY-MM-DD | decision | why`

- 2026-07-13 | Host ports 25432/28000/23000 | Avoid collisions with FactoryPulse and common local stacks
- 2026-07-13 | Bundle a weighted ACS-like microdata sample under `data/census/sample.jsonl` | Offline demos/CI without downloading full PUMS on developer machines
- 2026-07-13 | Default `SC_OFFLINE_LLM=1` with seeded persona/response generators | CI and showcase work without API keys; live providers when keys set
- 2026-07-13 | Accent rose `#f43f5e` per design system for SimCrowd | Project identity
- 2026-07-13 | GitHub Pages static export with studio demo mode | Showcase without hosting FastAPI; full stack via `make demo` elsewhere
- 2026-07-13 | Langfuse optional / deferred in compose | Keep M3 self-contained; cost logged as estimate in offline mode
- 2026-07-13 | Verifier counts hot interest over full cited persona_id lists | Keep cited counts recomputable 1:1 from raw responses
- 2026-07-13 | Stratified PPS quotas on age_bin x region x education x income_bin | Keeps whole-record joints while meeting the 3pp marginal realism unit test at n=200

- 2026-07-23 | Bundle data/pew/sample_scorecard.json and fall back from GET /scorecard | Compose and Pages demos can show a scorecard before make validate runs

- 2026-07-24 | Add scorecard CSV via pew_bench --csv and GET /scorecard.csv | Easy table refresh for validation writeups

- 2026-07-27 | Studio Download CSV uses live /scorecard.csv with client-side demo fallback | Closes the remaining scorecard export UX gap

- 2026-07-29 | Show scorecard source badge in studio (demo/sample/artifacts) | Makes validate vs bundled fallback obvious in the UI

- 2026-07-30 | Persist studio concept selection in localStorage | Keeps last concept across refreshes with invalid-path fallback

- 2026-07-31 | Reset control clears saved concept preference | Restores default concept chip after localStorage persist

- 2026-08-03 | Persist studio panel size in localStorage | Remembers 20/40/80 choice across refreshes with invalid-value fallback

- 2026-08-04 | Show panel size in study metrics | Surfaces last-run size with current preference fallback

- 2026-08-05 | Label panel size as preference vs last run | Clarifies whether metrics show chip selection or completed run

- 2026-08-06 | Note next-run panel size when chips differ from last run | Keeps last-run value while surfacing the upcoming size
