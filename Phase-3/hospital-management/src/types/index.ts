export interface User {
  id: string;
  username: string;
  email: string;
  role: 'Admin' | 'Doctor' | 'Patient';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Patient {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  gender: 'M' | 'F';
  address?: string;
  email: string;
  phone: string;
  created_at: string;
  updated_at: string;
}

export interface Doctor {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  department_id: string;
  phone: string;
  specialization: string;
  qualification: string;
  experience_years: number;
  created_at: string;
  updated_at: string;
}

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  schedule_id: string;
  status: 'Scheduled' | 'Completed' | 'Cancelled' | 'No-Show';
}

export interface MedicalRecord {
  id: string;
  patient_id: string;
  appointment_id?: string;
  department_id?: string;
  diagnosis: string;
  prescription: string;
  notes?: string;
  visit_date: string;
  date_created: string;
  updated_at: string;
}

export interface Department {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Schedule {
  id: string;
  doctor_id: string;
  datetime: string;
  duration: number;
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