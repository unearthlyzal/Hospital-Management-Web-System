import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';  // Update this with your Flask backend URL

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auth endpoints
export const auth = {
    login: (username: string, password: string) => 
        api.post('/auth/login', { username, password }),
    register: (userData: any) => 
        api.post('/auth/register', userData),
};

// Users endpoints
export const users = {
    getProfile: () => api.get('/users/profile'),
    updateProfile: (data: any) => api.put('/users/profile', data),
};

// Appointments endpoints
export const appointments = {
    getAll: () => api.get('/appointments'),
    getById: (id: string) => api.get(`/appointments/${id}`),
    create: (data: any) => api.post('/appointments', data),
    update: (id: string, data: any) => api.put(`/appointments/${id}`, data),
    delete: (id: string) => api.delete(`/appointments/${id}`),
};

// Departments endpoints
export const departments = {
    getAll: () => api.get('/departments'),
    getById: (id: string) => api.get(`/departments/${id}`),
};

// Export the api instance for other custom requests
export default api; 