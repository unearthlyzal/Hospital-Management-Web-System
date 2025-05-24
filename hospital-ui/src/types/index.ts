export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'doctor' | 'patient';
  first_name: string;
  last_name: string;
  doctor?: Doctor;
  patient?: Patient;
}

export interface Doctor {
  id: number;
  user_id: number;
  department_id: number;
  specialization: string;
  qualification: string;
  experience_years: number;
}

export interface Patient {
  id: number;
  user_id: number;
  date_of_birth: string;
  blood_group: string;
  gender: string;
  phone: string;
  address: string;
}

export interface Availability {
  id: number;
  doctor_id: number;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export interface Appointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  schedule_id: number;
  status: 'scheduled' | 'completed' | 'cancelled';
  date: string;
}

export interface MedicalRecord {
  id: number;
  patient_id: number;
  doctor_id: number;
  appointment_id: number;
  diagnosis: string;
  prescription: string;
  notes: string;
  record_date: string;
}

export interface Department {
  id: number;
  name: string;
  description: string;
}

export interface Schedule {
  id: number;
  doctor_id: number;
  day: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
} 