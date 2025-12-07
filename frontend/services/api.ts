import axios from 'axios';

// Guard import.meta.env access so TypeScript/SSR builds don't fail
declare const __VITE_ENV__ : any;
const env = (typeof import.meta !== 'undefined' && (import.meta as any).env) || __VITE_ENV__ || {};

// Development: Use direct backend URL to bypass Vite proxy issues
// Production: set VITE_API_URL in your environment/build (e.g. VITE_API_URL=https://api.example.com)
let API_BASE_URL: string;
if (env.VITE_API_URL !== undefined && env.VITE_API_URL !== null && env.VITE_API_URL !== '') {
  API_BASE_URL = env.VITE_API_URL;
} else if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
  // BYPASS Vite proxy - connect directly to backend to avoid proxy timeout issues
  API_BASE_URL = 'http://localhost:9000';
} else {
  // Fallback (use explicit localhost backend if nothing else provided)
  API_BASE_URL = 'http://localhost:9000';
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const token = localStorage.getItem('token');
        if (token) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, { token });
          const newToken = response.data.token;
          
          localStorage.setItem('token', newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;