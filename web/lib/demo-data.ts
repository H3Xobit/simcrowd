export type PersonaCard = {
  id: string;
  age: number;
  region: string;
  tech_segment: string;
  income_bin: string;
  occupation: string;
};

export type StudySummary = {
  study_id: string;
  n: number;
  attention_pass_rate: number;
  consistency_rate: number;
  cost_usd: number;
  report_id: string;
  verification_ok: boolean;
};

export type ReportRow = {
  id: string;
  study_id: string;
  summary: string;
  insights: { segment: string; text: string; count: number; persona_ids: string[] }[];
  objections: { theme: string; count: number }[];
  pricing: Record<string, unknown>;
  attention_pass_rate: number;
  cost_usd: number;
  verification_ok: boolean;
};

export type Scorecard = {
  mean_mae: number;
  mean_js: number;
  directional_agreement_rate: number;
  questions: {
    question_id: string;
    mae: number;
    js: number;
    directional_agreement: boolean;
    truth_top: string;
    synth_top: string | null;
  }[];
};

export const DEMO_PERSONAS: PersonaCard[] = [
  { id: "P0001", age: 34, region: "West", tech_segment: "Early adopter", income_bin: "75-150k", occupation: "STEM" },
  { id: "P0002", age: 52, region: "South", tech_segment: "Mainstream", income_bin: "35-75k", occupation: "Service" },
  { id: "P0003", age: 28, region: "Northeast", tech_segment: "Early adopter", income_bin: "75-150k", occupation: "Professional" },
  { id: "P0004", age: 61, region: "Midwest", tech_segment: "Low", income_bin: "<35k", occupation: "Retired" },
  { id: "P0005", age: 41, region: "West", tech_segment: "Mainstream", income_bin: "150k+", occupation: "Manager" },
  { id: "P0006", age: 23, region: "South", tech_segment: "Early adopter", income_bin: "35-75k", occupation: "Student" },
];

export const DEMO_STUDY: StudySummary = {
  study_id: "study_fintech_survey",
  n: 40,
  attention_pass_rate: 0.9,
  consistency_rate: 1.0,
  cost_usd: 0.08,
  report_id: "demo-report-001",
  verification_ok: true,
};

export const DEMO_REPORT: ReportRow = {
  id: "demo-report-001",
  study_id: "study_fintech_survey",
  summary:
    "Survey `Pulse Budget concept survey` with n=40. Attention pass rate=0.90. Early adopters lean interested; price and trust dominate objections.",
  insights: [
    {
      segment: "Early adopter|75-150k|West",
      text: "In segment Early adopter|75-150k|West, 6 of 8 respondents lean very/extremely interested.",
      count: 6,
      persona_ids: ["P0001", "P0003"],
    },
    {
      segment: "Low|<35k|Midwest",
      text: "In segment Low|<35k|Midwest, 1 of 5 respondents lean very/extremely interested.",
      count: 1,
      persona_ids: ["P0004"],
    },
  ],
  objections: [
    { theme: "trust_privacy", count: 14 },
    { theme: "price", count: 11 },
  ],
  pricing: { ok: true, optimal_price_point: 12, indifference_price_point: 12, n: 40 },
  attention_pass_rate: 0.9,
  cost_usd: 0.08,
  verification_ok: true,
};

export const DEMO_SCORECARD: Scorecard = {
  mean_mae: 0.12,
  mean_js: 0.04,
  directional_agreement_rate: 0.75,
  questions: [
    {
      question_id: "tech_ai_interest",
      mae: 0.09,
      js: 0.03,
      directional_agreement: true,
      truth_top: "Somewhat interested",
      synth_top: "Somewhat interested",
    },
    {
      question_id: "tech_privacy_worry",
      mae: 0.11,
      js: 0.04,
      directional_agreement: true,
      truth_top: "Somewhat worried",
      synth_top: "Somewhat worried",
    },
    {
      question_id: "fin_emergency_400",
      mae: 0.18,
      js: 0.06,
      directional_agreement: false,
      truth_top: "Yes",
      synth_top: "No",
    },
    {
      question_id: "tech_social_daily",
      mae: 0.1,
      js: 0.03,
      directional_agreement: true,
      truth_top: "Yes",
      synth_top: "Yes",
    },
  ],
};

export const DEMO_EVAL = {
  timestamp: "2026-07-13T05:00:00Z",
  n: 20,
  panel_max_marginal_error: 0.028,
  consistency_rate: 1.0,
  attention_pass_rate: 0.9,
  report_verification_ok: true,
  reproducible: true,
  pew_mean_mae: 0.14,
  pew_directional_agreement_rate: 0.75,
  cost_per_study_usd: 0.04,
  latency_s: 0.4,
};
