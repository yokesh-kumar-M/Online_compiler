import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: baseURL,
  headers: { 'Content-Type': 'application/json' },
});

// Intercept requests to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercept responses for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/v1/auth/token/refresh/', {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', data.access);
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          return api(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.reload();
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (data) => api.post('/auth/login/', data),
  register: (data) => api.post('/auth/register/', data),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  profile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
};

// Compiler API
export const compilerAPI = {
  execute: (data) => api.post('/compiler/execute/', data),
  languages: () => api.get('/compiler/languages/'),
  examples: () => api.get('/compiler/examples/'),
  health: () => api.get('/compiler/health/'),
};

// Snippets API
export const snippetsAPI = {
  list: (params) => api.get('/snippets/', { params }),
  get: (id) => api.get(`/snippets/${id}/`),
  create: (data) => api.post('/snippets/', data),
  update: (id, data) => api.put(`/snippets/${id}/`, data),
  delete: (id) => api.delete(`/snippets/${id}/`),
  star: (id) => api.post(`/snippets/${id}/star/`),
  fork: (id) => api.post(`/snippets/${id}/fork/`),
  bySlug: (slug) => api.get(`/snippets/by-slug/${slug}/`),
};

export default api;
