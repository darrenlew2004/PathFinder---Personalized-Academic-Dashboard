import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../services/api';

export interface Student {
  id: string;
  studentId: string;
  name: string;
  email: string;
  gpa: number;
  semester: number;
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
  async (credentials: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/login', credentials);
      if (response?.data?.token) {
        localStorage.setItem('token', response.data.token);
      }
      return response.data;
    } catch (error) {
      const err = error as any;
      return rejectWithValue(err?.response?.data ?? String(err));
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (
    userData: {
      studentId: string;
      name: string;
      email: string;
      password: string;
      gpa?: number;
      semester?: number;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.post('/auth/register', userData);
      if (response?.data?.token) {
        localStorage.setItem('token', response.data.token);
      }
      return response.data;
    } catch (error) {
      const err = error as any;
      return rejectWithValue(err?.response?.data ?? String(err));
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
      state.user = action.payload.user ?? action.payload;
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