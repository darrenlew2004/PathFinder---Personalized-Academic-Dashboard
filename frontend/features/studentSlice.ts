import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../services/api';

export interface Subject {
  id: number;
  programme_code: string;
  subject_code: string;
  subject_name: string;
  subject_type: string;
  credit: number;
  semester: number;
  prerequisite: any;
  core_subject_in_programme: any;
  level: number;
}

export interface Student {
  id: number;
  name: string;
  ic: string;
  programmecode: string;
  program: string;
  overallcgpa: number;
  overallcavg: number;
  year: number;
  sem: number;
  status: string;
  graduated: boolean;
  cohort: string;
  gender: string;
  race: string;
  country: string;
  yearonecgpa: number;
  awardclassification: string;
  broadsheetyear: number;
  cavg: number;
  finanicalaid: string;
  qualifications: any;
  sponsorname: string;
  subjects: any;
  yearonaverage: number;
}

export interface StudentWithSubjects {
  student: Student;
  subjects: Subject[];
}

interface StudentsState {
  currentStudent: Student | null;
  studentWithSubjects: StudentWithSubjects | null;
  allStudents: Student[];
  loading: boolean;
  error: string | null;
}

const initialState: StudentsState = {
  currentStudent: null,
  studentWithSubjects: null,
  allStudents: [],
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
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.error || 'Failed to fetch student data');
    }
  }
);

export const fetchStudentWithSubjects = createAsyncThunk(
  'students/fetchWithSubjects',
  async (studentId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/api/students/${studentId}/subjects`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.error || 'Failed to fetch student subjects');
    }
  }
);

export const fetchAllStudents = createAsyncThunk(
  'students/fetchAll',
  async (limit: number = 50, { rejectWithValue }) => {
    try {
      const response = await api.get(`/api/students/list?limit=${limit}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.error || 'Failed to fetch students');
    }
  }
);

const studentsSlice = createSlice({
  name: 'students',
  initialState,
  reducers: {
    clearStudentData: (state) => {
      state.currentStudent = null;
      state.studentWithSubjects = null;
      state.allStudents = [];
    },
    setCurrentStudent: (state, action) => {
      state.currentStudent = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Current Student
      .addCase(fetchStudentStats.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStudentStats.fulfilled, (state, action) => {
        state.loading = false;
        state.currentStudent = action.payload;
        state.error = null;
      })
      .addCase(fetchStudentStats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Student with Subjects
      .addCase(fetchStudentWithSubjects.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchStudentWithSubjects.fulfilled, (state, action) => {
        state.loading = false;
        state.studentWithSubjects = action.payload;
      })
      .addCase(fetchStudentWithSubjects.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch All Students
      .addCase(fetchAllStudents.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAllStudents.fulfilled, (state, action) => {
        state.loading = false;
        state.allStudents = action.payload;
      })
      .addCase(fetchAllStudents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearStudentData, setCurrentStudent } = studentsSlice.actions;
export default studentsSlice.reducer;