import api from './api';

export interface VariantsResponse {
  variants: string[];
  count: number;
}

export interface CourseInfo {
  subject_code: string;
  subject_name: string;
  credit: number;
  semester_offering?: number;
  category: string;
  elective_group?: string;
  prerequisites: string[];
  is_placeholder: boolean;
}

export interface ElectiveGroupInfo {
  group_code: string;
  year_level?: number;
  options: CourseInfo[];
}

export interface ElectivesResponse {
  variant: string;
  elective_groups: Record<string, ElectiveGroupInfo>;
}

export interface ProgressRequest {
  intake: string;
  entry_type: string; // normal | direct | precalc
  completed_codes: string[];
}

export interface ProgressResponse {
  completed_credits: number;
  total_credits: number;
  outstanding_credits: number;
  core_remaining: string[];
  discipline_elective_placeholders_remaining: string[];
  free_elective_placeholders_remaining: string[];
  either_pairs_remaining: string[][];
  percent_complete: number;
}

export interface WhatIfRequest extends ProgressRequest {
  planned_codes: string[];
  cgpa: number;
  attendance: number;
  gpa_trend?: number;
}

export interface CourseRiskResponse {
  subject_code: string;
  subject_name: string;
  predicted_risk: 'low'|'medium'|'high'|string;
  numeric_score: number;
  factors: Record<string, number>;
}

export interface WhatIfResponse {
  selected_subject_codes: string[];
  total_credits: number;
  aggregated_risk_score: number;
  risk_band: 'low'|'medium'|'high'|string;
  per_course: CourseRiskResponse[];
}

export async function listVariants(): Promise<VariantsResponse> {
  const { data } = await api.get<VariantsResponse>('/api/catalogue/variants');
  return data;
}

export async function getElectives(variantKey: string): Promise<ElectivesResponse> {
  const { data } = await api.get<ElectivesResponse>(`/api/catalogue/variant/${variantKey}/electives`);
  return data;
}

export async function computeProgress(req: ProgressRequest): Promise<ProgressResponse> {
  const { data } = await api.post<ProgressResponse>('/api/catalogue/progress', req);
  return data;
}

export async function whatIf(req: WhatIfRequest): Promise<WhatIfResponse> {
  const { data } = await api.post<WhatIfResponse>('/api/catalogue/what-if', req);
  return data;
}

export async function getStudentProgress(intake: string, entryType: string): Promise<ProgressResponse> {
  const { data } = await api.get<ProgressResponse>(`/api/catalogue/student/progress?intake=${encodeURIComponent(intake)}&entry_type=${encodeURIComponent(entryType)}`);
  return data;
}
