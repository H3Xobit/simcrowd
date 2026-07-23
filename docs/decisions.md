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
