import { configureStore } from '@reduxjs/toolkit';
import authReducer from './features/authSlice';
import studentsReducer from './features/studentSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    students: studentsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;