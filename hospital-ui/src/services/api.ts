import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
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

api.interceptors.request.use((config: AxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`
    };
  }
  return config;
});

type LoginResponse = ApiResponse<{ token: string; user: User }>;
type UserResponse = ApiResponse<User>;
type UsersResponse = ApiResponse<User[]>;
type DoctorResponse = ApiResponse<Doctor>;
type DoctorsResponse = ApiResponse<Doctor[]>;
type PatientResponse = ApiResponse<Patient>;
type PatientsResponse = ApiResponse<Patient[]>;
type AppointmentResponse = ApiResponse<Appointment>;
type AppointmentsResponse = ApiResponse<Appointment[]>;
type MedicalRecordResponse = ApiResponse<MedicalRecord>;
type MedicalRecordsResponse = ApiResponse<MedicalRecord[]>;
type DepartmentResponse = ApiResponse<Department>;
type DepartmentsResponse = PaginatedResponse<Department>;
type ScheduleResponse = ApiResponse<Schedule>;
type SchedulesResponse = ApiResponse<Schedule[]>;

export const auth = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', { username, password });
    return response.data;
  },
  register: async (userData: Partial<User>): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/register', userData);
    return response.data;
  },
  getProfile: async (): Promise<UserResponse> => {
    const response = await api.get<UserResponse>('/users/profile');
    return response.data;
  },
};

export const users = {
  getAll: async (): Promise<UsersResponse> => {
    const response = await api.get<UsersResponse>('/users');
    return response.data;
  },
  getById: async (id: number): Promise<UserResponse> => {
    const response = await api.get<UserResponse>(`/users/${id}`);
    return response.data;
  },
  create: async (data: Partial<User>): Promise<UserResponse> => {
    const response = await api.post<UserResponse>('/users', data);
    return response.data;
  },
  update: async (id: number, data: Partial<User>): Promise<UserResponse> => {
    const response = await api.put<UserResponse>(`/users/${id}`, data);
    return response.data;
  },
  delete: async (id: number): Promise<void> => {
    await api.delete(`/users/${id}`);
  },
};

export const doctors = {
  getAll: async (): Promise<DoctorsResponse> => {
    const response = await api.get<DoctorsResponse>('/doctors');
    return response.data;
  },
  getById: async (id: number): Promise<DoctorResponse> => {
    const response = await api.get<DoctorResponse>(`/doctors/${id}`);
    return response.data;
  },
  create: async (data: Partial<Doctor>): Promise<DoctorResponse> => {
    const response = await api.post<DoctorResponse>('/doctors', data);
    return response.data;
  },
  update: async (id: number, data: Partial<Doctor>): Promise<DoctorResponse> => {
    const response = await api.put<DoctorResponse>(`/doctors/${id}`, data);
    return response.data;
  },
  delete: async (id: number): Promise<void> => {
    await api.delete(`/doctors/${id}`);
  },
  getAvailabilities: async (doctorId: number): Promise<SchedulesResponse> => {
    const response = await api.get<SchedulesResponse>(`/doctors/${doctorId}/availabilities`);
    return response.data;
  },
  createAvailability: async (doctorId: number, data: Partial<Schedule>): Promise<ScheduleResponse> => {
    const response = await api.post<ScheduleResponse>(`/doctors/${doctorId}/availabilities`, data);
    return response.data;
  },
  updateAvailability: async (doctorId: number, availabilityId: number, data: Partial<Schedule>): Promise<ScheduleResponse> => {
    const response = await api.put<ScheduleResponse>(`/doctors/${doctorId}/availabilities/${availabilityId}`, data);
    return response.data;
  },
  deleteAvailability: async (doctorId: number, availabilityId: number): Promise<void> => {
    await api.delete(`/doctors/${doctorId}/availabilities/${availabilityId}`);
  },
};

export const patients = {
  getAll: async () => {
    const response = await api.get<ApiResponse<Patient[]>>('/patients');
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get<ApiResponse<Patient>>(`/patients/${id}`);
    return response.data;
  },
  create: (data: Partial<Patient>) => 
    api.post<ApiResponse<Patient>>('/patients', data),
  update: (id: number, data: Partial<Patient>) => 
    api.put<ApiResponse<Patient>>(`/patients/${id}`, data),
  delete: (id: number) => 
    api.delete<ApiResponse<void>>(`/patients/${id}`),
};

export const appointments = {
  getAll: async () => {
    const response = await api.get<ApiResponse<Appointment[]>>('/appointments');
    return response.data;
  },
  getById: (id: number) => 
    api.get<ApiResponse<Appointment>>(`/appointments/${id}`),
  create: (data: Partial<Appointment>) => 
    api.post<ApiResponse<Appointment>>('/appointments', data),
  update: (id: number, data: Partial<Appointment>) => 
    api.put<ApiResponse<Appointment>>(`/appointments/${id}`, data),
  delete: (id: number) => 
    api.delete<ApiResponse<void>>(`/appointments/${id}`),
  getPatientAppointments: (patientId: number) => 
    api.get<ApiResponse<{ upcoming: Appointment[]; past: Appointment[] }>>(`/patients/${patientId}/appointments/sorted`),
  getDoctorAppointments: async (doctorId: number) => {
    const response = await api.get<ApiResponse<{ upcoming: Appointment[]; past: Appointment[] }>>(`/appointments/doctor/${doctorId}`);
    return response.data;
  },
};

export const medicalRecords = {
  getAll: async () => {
    const response = await api.get<ApiResponse<MedicalRecord[]>>('/medical-records');
    return response.data;
  },
  getById: (id: number) => 
    api.get<ApiResponse<MedicalRecord>>(`/medical-records/${id}`),
  create: (data: Partial<MedicalRecord>) => 
    api.post<ApiResponse<MedicalRecord>>('/medical-records', data),
  update: (id: number, data: Partial<MedicalRecord>) => 
    api.put<ApiResponse<MedicalRecord>>(`/medical-records/${id}`, data),
  delete: (id: number) => 
    api.delete<ApiResponse<void>>(`/medical-records/${id}`),
  getPatientRecords: async (patientId: number) => {
    const response = await api.get<ApiResponse<MedicalRecord[]>>(`/medical-records/patient/${patientId}`);
    return response.data;
  },
  getDoctorRecords: (doctorId: number) => 
    api.get<ApiResponse<MedicalRecord[]>>(`/doctors/${doctorId}/medical-records`),
};

export const departments = {
  getAll: () => 
    api.get<PaginatedResponse<Department>>('/departments'),
  getById: (id: number) => 
    api.get<ApiResponse<Department>>(`/departments/${id}`),
  create: (data: Partial<Department>) => 
    api.post<ApiResponse<Department>>('/departments', data),
  update: (id: number, data: Partial<Department>) => 
    api.put<ApiResponse<Department>>(`/departments/${id}`, data),
  delete: (id: number) => 
    api.delete<ApiResponse<void>>(`/departments/${id}`),
};

export const schedules = {
  getAll: () => 
    api.get<PaginatedResponse<Schedule>>('/schedules'),
  getById: (id: number) => 
    api.get<ApiResponse<Schedule>>(`/schedules/${id}`),
  create: (data: Partial<Schedule>) => 
    api.post<ApiResponse<Schedule>>('/schedules', data),
  update: (id: number, data: Partial<Schedule>) => 
    api.put<ApiResponse<Schedule>>(`/schedules/${id}`, data),
  delete: (id: number) => 
    api.delete<ApiResponse<void>>(`/schedules/${id}`),
};

export default api; 