// Mirrors Pydantic schemas from backend/app/schemas.py

export interface InstitutionSummary {
  id: number;
  name: string;
  type: string | null;
  city: string | null;
  state: string | null;
  lat: number | null;
  lon: number | null;
  trial_count: number;
  kol_count: number;
  disease_burden_rate: number | null;
}

export interface KOLSummary {
  npi: string;
  name: string;
  specialty: string | null;
  state: string | null;
  city: string | null;
  institution_name: string | null;
  kol_score: number;
  trial_score: number;
  pub_score: number;
  activity_score: number;
  geographic_reach_score: number;
  payment_total_usd: number;
  payment_company_count: number;
}

export interface TrialRef {
  nct_id: string;
  title: string | null;
  phase: string | null;
  status: string | null;
  sponsor: string | null;
  start_date: string | null;
  role: string | null;
}

export interface PublicationRef {
  pmid: string;
  title: string | null;
  journal: string | null;
  year: number | null;
  citation_count: number;
  author_order: number | null;
}

export interface PaymentRecord {
  id: number;
  company_name: string | null;
  amount_usd: number;
  nature_of_payment: string | null;
  year: number | null;
  record_id: string | null;
}

export interface KOLDetail {
  npi: string;
  name: string;
  specialty: string | null;
  state: string | null;
  city: string | null;
  institution: InstitutionSummary | null;
  kol_score: number;
  trial_score: number;
  pub_score: number;
  activity_score: number;
  geographic_reach: number;
  geographic_reach_score: number;
  payment_total_usd: number;
  payment_company_count: number;
  trials: TrialRef[];
  publications: PublicationRef[];
  payments: PaymentRecord[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: "kol" | "institution";
  score: number;
  state: string | null;
  institution: string | null;
}

export interface GraphLink {
  source: string;
  target: string;
  type: "investigates" | "co_investigates" | "affiliated_with" | "co_authored";
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface KOLListResponse {
  total: number;
  page: number;
  page_size: number;
  items: KOLSummary[];
}

export interface DiseaseBurdenRecord {
  state: string;
  cancer_type: string;
  year: number;
  incidence_rate: number | null;
  mortality_rate: number | null;
}

export interface ExplanationResponse {
  npi: string;
  rationale: string;
  engagement_type: string;
  compliance_note: string;
  cached: boolean;
}

// Filter state shared across pages
export interface KOLFilters {
  state: string;
  minScore: number;
  phase: string;
  recruitingOnly: boolean;
}
