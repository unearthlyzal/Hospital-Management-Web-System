import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

// Layout
import Layout from '../components/Layout';

// Public Pages
import Login from '../pages/auth/Login';
import Register from '../pages/auth/Register';

// Patient Pages
import PatientDashboard from '../pages/patient/Dashboard';
import PatientProfile from '../pages/patient/Profile';
import BookAppointment from '../pages/patient/BookAppointment';

// Doctor Pages
import DoctorDashboard from '../pages/doctor/Dashboard';
import DoctorProfile from '../pages/doctor/Profile';
import DoctorAvailability from '../pages/doctor/Availability';
import MedicalRecords from '../pages/doctor/MedicalRecords';

// Admin Pages
import AdminDashboard from '../pages/admin/Dashboard';
import DepartmentManagement from '../pages/admin/DepartmentManagement';
import UserManagement from '../pages/admin/UserManagement';

interface ProtectedRouteProps {
  children: React.ReactNode;
  roles?: string[];
}

const ProtectedRoute = ({ children, roles }: ProtectedRouteProps) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (roles && !roles.includes(user?.role || '')) {
    return <Navigate to="/" />;
  }

  return <>{children}</>;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Patient Routes */}
        <Route
          path="patient"
          element={
            <ProtectedRoute roles={['patient']}>
              <PatientDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="patient/profile"
          element={
            <ProtectedRoute roles={['patient']}>
              <PatientProfile />
            </ProtectedRoute>
          }
        />
        <Route
          path="patient/book-appointment"
          element={
            <ProtectedRoute roles={['patient']}>
              <BookAppointment />
            </ProtectedRoute>
          }
        />

        {/* Doctor Routes */}
        <Route
          path="doctor"
          element={
            <ProtectedRoute roles={['doctor']}>
              <DoctorDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="doctor/profile"
          element={
            <ProtectedRoute roles={['doctor']}>
              <DoctorProfile />
            </ProtectedRoute>
          }
        />
        <Route
          path="doctor/availability"
          element={
            <ProtectedRoute roles={['doctor']}>
              <DoctorAvailability />
            </ProtectedRoute>
          }
        />
        <Route
          path="doctor/medical-records"
          element={
            <ProtectedRoute roles={['doctor']}>
              <MedicalRecords />
            </ProtectedRoute>
          }
        />

        {/* Admin Routes */}
        <Route
          path="admin"
          element={
            <ProtectedRoute roles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/departments"
          element={
            <ProtectedRoute roles={['admin']}>
              <DepartmentManagement />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/users"
          element={
            <ProtectedRoute roles={['admin']}>
              <UserManagement />
            </ProtectedRoute>
          }
        />

        {/* Redirect to role-specific dashboard */}
        <Route
          index
          element={
            <ProtectedRoute>
              <Navigate to="/patient" replace />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes; 