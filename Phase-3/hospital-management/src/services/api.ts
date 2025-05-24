import axios, { InternalAxiosRequestConfig } from 'axios';
import {
  User,
  Doctor,
  Patient,
  Appointment,
  MedicalRecord,
  Department,
  Schedule,
  ApiResponse,
  PaginatedResponse
} from '../types';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
});

// Add token to requests
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const auth = {
  login: async (username: string, password: string): Promise<ApiResponse<{ token: string; user: User }>> => {
    const response = await api.post<ApiResponse<{ token: string; user: User }>>('/auth/login', { username, password });
    return response.data;
  },
  register: async (userData: Partial<User>): Promise<ApiResponse<{ token: string; user: User }>> => {
    const response = await api.post<ApiResponse<{ token: string; user: User }>>('/auth/register', userData);
    return response.data;
  },
};

export const users = {
  getProfile: async (): Promise<ApiResponse<User>> => {
    const response = await api.get<ApiResponse<User>>('/users/profile');
    return response.data;
  },
  update: async (id: number, data: Partial<User>): Promise<ApiResponse<User>> => {
    const response = await api.put<ApiResponse<User>>(`/users/${id}`, data);
    return response.data;
  },
};

export const appointments = {
  getAll: async (): Promise<ApiResponse<Appointment[]>> => {
    const response = await api.get<ApiResponse<Appointment[]>>('/appointments');
    return response.data;
  },
  create: async (data: Partial<Appointment>): Promise<ApiResponse<Appointment>> => {
    const response = await api.post<ApiResponse<Appointment>>('/appointments', data);
    return response.data;
  },
  update: async (id: number, data: Partial<Appointment>): Promise<ApiResponse<Appointment>> => {
    const response = await api.put<ApiResponse<Appointment>>(`/appointments/${id}`, data);
    return response.data;
  },
  cancel: async (id: number): Promise<ApiResponse<void>> => {
    const response = await api.delete<ApiResponse<void>>(`/appointments/${id}`);
    return response.data;
  },
};

export const medicalRecords = {
  getAll: async (): Promise<ApiResponse<MedicalRecord[]>> => {
    const response = await api.get<ApiResponse<MedicalRecord[]>>('/medical-records');
    return response.data;
  },
  create: async (data: Partial<MedicalRecord>): Promise<ApiResponse<MedicalRecord>> => {
    const response = await api.post<ApiResponse<MedicalRecord>>('/medical-records', data);
    return response.data;
  },
  update: async (id: number, data: Partial<MedicalRecord>): Promise<ApiResponse<MedicalRecord>> => {
    const response = await api.put<ApiResponse<MedicalRecord>>(`/medical-records/${id}`, data);
    return response.data;
  },
};

export default api; 