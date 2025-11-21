import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../services/api';

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

interface AuthState {
  user: Student | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  isAuthenticated: !!(typeof window !== 'undefined' && localStorage.getItem('token')),
  loading: false,
  error: null,
};

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { student_id: number }, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/login', credentials);
      if (response?.data?.token) {
        localStorage.setItem('token', response.data.token);
      }
      return response.data;
    } catch (error) {
      const err = error as any;
      return rejectWithValue(err?.response?.data?.detail || err?.response?.data || String(err));
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (_userData: { student_id: number; name: string; ic: string }, { rejectWithValue }) => {
    try {
      // Registration not supported - database is read-only
      return rejectWithValue('Registration is not available. Please contact your administrator.');
    } catch (error) {
      const err = error as any;
      return rejectWithValue(err?.response?.data?.detail || err?.response?.data || String(err));
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout(state) {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      localStorage.removeItem('token');
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder.addCase(login.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(login.fulfilled, (state, action: PayloadAction<any>) => {
      state.loading = false;
      state.user = action.payload.student ?? action.payload.user ?? action.payload;
      state.token = action.payload.token ?? state.token;
      state.isAuthenticated = !!state.token;
      state.error = null;
    });
    builder.addCase(login.rejected, (state, action) => {
      state.loading = false;
      state.error = (action.payload as any) || 'Login failed';
    });

    // Register
    builder.addCase(register.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(register.fulfilled, (state, action: PayloadAction<any>) => {
      state.loading = false;
      state.user = action.payload.user ?? action.payload;
      state.token = action.payload.token ?? state.token;
      state.isAuthenticated = !!state.token;
      state.error = null;
    });
    builder.addCase(register.rejected, (state, action) => {
      state.loading = false;
      state.error = (action.payload as any) || 'Registration failed';
    });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;