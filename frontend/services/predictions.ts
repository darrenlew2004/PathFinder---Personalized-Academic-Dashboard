import { api } from './api';

export interface PrerequisitePerformance {
  subject_code: string;
  subject_name: string;
  grade: string;
  grade_points: number;
  weight: number;
  impact_score: number;
}

export interface SubjectPrediction {
  subject_code: string;
  subject_name: string;
  risk_level: 'low' | 'medium' | 'high' | 'very_high' | 'unknown';
  predicted_success_probability: number;
  weighted_prereq_gpa: number;
  prereq_performance: PrerequisitePerformance[];
  missing_prereqs: string[];
  recommendation: string;
  cohort_pass_rate: number | null;
  cohort_avg_score: number | null;
}

export interface StudentPredictionReport {
  student_id: number;
  current_gpa: number;
  predictions: SubjectPrediction[];
  high_risk_subjects: string[];
  recommended_order: string[];
}

export interface PrerequisiteChain {
  subject_code: string;
  subject_name: string;
  direct_prerequisites: Array<{ code: string; name: string; weight: number }>;
  full_chain: Array<{ code: string; name: string; depth: number }>;
}

export interface CohortStats {
  subject_code: string;
  subject_name: string;
  pass_rate: number | null;
  avg_score: number | null;
  avg_gpa: number | null;
  total_students: number;
}

/**
 * Get prediction for a single subject for a specific student
 */
export async function getSubjectPrediction(
  studentId: number,
  subjectCode: string
): Promise<SubjectPrediction> {
  const response = await api.get<SubjectPrediction>(
    `/api/predictions/students/${studentId}/subject/${subjectCode}`
  );
  return response.data;
}

/**
 * Get predictions for multiple subjects for a specific student
 */
export async function getMultipleSubjectPredictions(
  studentId: number,
  subjectCodes: string[]
): Promise<StudentPredictionReport> {
  const response = await api.post<StudentPredictionReport>(
    `/api/predictions/students/${studentId}/subjects`,
    { subject_codes: subjectCodes }
  );
  return response.data;
}

/**
 * Get prediction for a single subject for the current logged-in student
 */
export async function getCurrentStudentSubjectPrediction(
  subjectCode: string
): Promise<SubjectPrediction> {
  const response = await api.get<SubjectPrediction>(
    `/api/predictions/current/subject/${subjectCode}`
  );
  return response.data;
}

/**
 * Get predictions for multiple subjects for the current logged-in student
 */
export async function getCurrentStudentMultiplePredictions(
  subjectCodes: string[]
): Promise<StudentPredictionReport> {
  const response = await api.post<StudentPredictionReport>(
    `/api/predictions/current/subjects`,
    { subject_codes: subjectCodes }
  );
  return response.data;
}

/**
 * Get the prerequisite chain for a subject
 */
export async function getPrerequisiteChain(
  subjectCode: string
): Promise<PrerequisiteChain> {
  const response = await api.get<PrerequisiteChain>(
    `/api/predictions/prerequisites/${subjectCode}`
  );
  return response.data;
}

/**
 * Get cohort statistics for a subject
 */
export async function getCohortStats(subjectCode: string): Promise<CohortStats> {
  const response = await api.get<CohortStats>(
    `/api/predictions/cohort-stats/${subjectCode}`
  );
  return response.data;
}

/**
 * Get cohort statistics for all subjects
 */
export async function getAllCohortStats(): Promise<CohortStats[]> {
  const response = await api.get<CohortStats[]>('/api/predictions/cohort-stats');
  return response.data;
}

/**
 * Get risk level color for display
 */
export function getRiskColor(riskLevel: string): 'success' | 'warning' | 'error' | 'info' {
  switch (riskLevel) {
    case 'low':
      return 'success';
    case 'medium':
      return 'warning';
    case 'high':
    case 'very_high':
      return 'error';
    default:
      return 'info';
  }
}

/**
 * Get risk level emoji for display
 */
export function getRiskEmoji(riskLevel: string): string {
  switch (riskLevel) {
    case 'low':
      return '✅';
    case 'medium':
      return '🟡';
    case 'high':
      return '🔶';
    case 'very_high':
      return '🔴';
    default:
      return 'ℹ️';
  }
}

/**
 * Format probability as percentage
 */
export function formatProbability(probability: number): string {
  return `${Math.round(probability * 100)}%`;
}
