import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../services/api';

export interface Course {
  id: string;
  courseCode: string;
  courseName: string;
  credits: number;
  difficulty: number;
  prerequisites: string[];
  description: string;
}

export interface Enrollment {
  id: string;
  studentId: string;
  courseId: string;
  semester: number;
  grade: string | null;
  status: 'ENROLLED' | 'COMPLETED' | 'FAILED' | 'DROPPED';
  attendanceRate: number;
}

export interface RiskPrediction {
  id: string;
  studentId: string;
  courseId: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence: number;
  factors: Record<string, number>;
  recommendations: string[];
  predictedGrade: string | null;
  createdAt: string;
}

export interface CourseProgress {
  course: Course;
  enrollment: Enrollment;
  riskPrediction: RiskPrediction | null;
}

export interface StudentStats {
  student: {
    id: string;
    studentId: string;
    name: string;
    email: string;
    gpa: number;
    semester: number;
  };
  currentCourses: CourseProgress[];
  completedCourses: number;
  totalCredits: number;
  averageAttendance: number;
  riskDistribution: Record<string, number>;
}

interface StudentsState {
  stats: StudentStats | null;
  courseProgress: CourseProgress[];
  riskPredictions: RiskPrediction[];
  loading: boolean;
  error: string | null;
}

const initialState: StudentsState = {
  stats: null,
  courseProgress: [],
  riskPredictions: [],
  loading: false,
  error: null,
};

export const fetchStudentStats = createAsyncThunk(
  'students/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/students/current');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch student stats');
    }
  }
);

export const fetchCourseProgress = createAsyncThunk(
  'students/fetchCourseProgress',
  async (studentId: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/api/students/${studentId}/progress`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch course progress');
    }
  }
);

export const fetchRiskPredictions = createAsyncThunk(
  'students/fetchRiskPredictions',
  async (studentId: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/api/students/${studentId}/risks`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch risk predictions');
    }
  }
);

const studentsSlice = createSlice({
  name: 'students',
  initialState,
  reducers: {
    clearStudentData: (state) => {
      state.stats = null;
      state.courseProgress = [];
      state.riskPredictions = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Student Stats
      .addCase(fetchStudentStats.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStudentStats.fulfilled, (state, action) => {
        state.loading = false;
        state.stats = action.payload;
        state.error = null;
      })
      .addCase(fetchStudentStats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Course Progress
      .addCase(fetchCourseProgress.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchCourseProgress.fulfilled, (state, action) => {
        state.loading = false;
        state.courseProgress = action.payload;
      })
      .addCase(fetchCourseProgress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Risk Predictions
      .addCase(fetchRiskPredictions.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchRiskPredictions.fulfilled, (state, action) => {
        state.loading = false;
        state.riskPredictions = action.payload;
      })
      .addCase(fetchRiskPredictions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearStudentData } = studentsSlice.actions;
export default studentsSlice.reducer;