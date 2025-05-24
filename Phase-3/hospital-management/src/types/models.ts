export interface User {
    id: string;
    username: string;
    email: string;
    role: string;
    is_active: boolean;
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
}

export interface Doctor {
    id: string;
    user_id: string;
    first_name: string;
    last_name: string;
    department_id: string;
    availability: Record<string, string>;
    phone: string;
}

export interface Appointment {
    id: string;
    patient_id: string;
    doctor_id: string;
    schedule_id: string;
    status: string;
}

export interface Department {
    id: string;
    name: string;
    description?: string;
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