// These shapes match what the Python backend sends (see api.py / agent.py).

export type SubQuestion = { question: string; search_query: string };

/** One live step from the agent, e.g. { step: "search", message: "Searching arXiv: ..." } */
export type AgentStep = {
  step: string;
  message: string;
  score?: number; // "coverage" steps
  missing?: string; // "coverage" steps
  papers?: string[]; // "filter" and "compare" steps
  top_scores?: number[]; // "filter" steps
  sub_questions?: SubQuestion[]; // "plan_done" step
};

/** A step plus the seconds since the run started (added by the frontend). */
export type TimedStep = AgentStep & { t: number };

export type Source = {
  number: number;
  title: string;
  year: number;
  section: string;
  arxiv_id: string;
  url: string;
  text: string;
};

export type ComparisonRow = {
  arxiv_id: string;
  title?: string;
  year?: number;
  problem?: string;
  method?: string;
  data_or_benchmarks?: string;
  key_results?: string;
  limitations?: string;
  error?: string;
};

export type ResearchResult = {
  topic: string;
  review: string;
  comparison: ComparisonRow[];
  sources: Source[];
  invalid_citations: number[];
  uncited_sentences: string[];
  sub_questions: { question: string; coverage: { score: number; missing: string }; papers_added: number }[];
  slug?: string;
};

export type Overview = {
  papers: number;
  chunks: number;
  most_recently_added: { title: string; year: number; arxiv_id: string }[];
};

export type Health = { status: string; llm_provider: string; llm_model: string; busy: boolean };

/** One row in the "past reviews" list. */
export type ReviewSummary = { slug: string; topic: string; sources: number; created: number };
