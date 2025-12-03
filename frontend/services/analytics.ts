import { api } from './api';

export interface SubjectBrief {
  subjectcode: string | null;
  subjectname: string | null;
  overallpercentage: number | null;
}

export interface StudentTermStat {
  term: string;
  avg_percentage: number | null;
  total_exams: number;
  pass_rate: number | null;
}

export interface StudentProfile {
  student_id: number;
  subjects_taken: number;
  terms_taken: number;
  current_gpa: number | null;
  avg_score: number | null;
  score_std: number | null;
  best_subject: SubjectBrief | null;
  worst_subject: SubjectBrief | null;
  avg_benchmark_delta: number | null;
  fails_count: number;
  retakes_count: number;
  score_trend_per_term: number | null;
  term_stats: StudentTermStat[];
}

export async function getStudentAnalytics(studentId: number): Promise<StudentProfile> {
  const response = await api.get<StudentProfile>(`/api/students/${studentId}/analytics`);
  return response.data;
}

export async function getCurrentStudentAnalytics(): Promise<StudentProfile> {
  const response = await api.get<StudentProfile>('/api/students/current/analytics');
  return response.data;
}
