import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  People as PeopleIcon,
  LocalHospital as DoctorIcon,
  Person as PatientIcon,
  Event as AppointmentIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { users, doctors, patients, appointments } from '../../services/api';

interface Stats {
  totalUsers: number;
  totalDoctors: number;
  totalPatients: number;
  totalAppointments: number;
}

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<Stats>({
    totalUsers: 0,
    totalDoctors: 0,
    totalPatients: 0,
    totalAppointments: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [usersRes, doctorsRes, patientsRes, appointmentsRes] = await Promise.all([
        users.getAll(),
        doctors.getAll(),
        patients.getAll(),
        appointments.getAll(),
      ]);

      setStats({
        totalUsers: usersRes.data.total,
        totalDoctors: doctorsRes.data.total,
        totalPatients: patientsRes.data.total,
        totalAppointments: appointmentsRes.data.total,
      });
    } catch (err: any) {
      setError('Failed to fetch statistics');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color }: any) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Icon sx={{ fontSize: 40, color }} />
          <Typography variant="h6" ml={2}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4">{value}</Typography>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={stats.totalUsers}
            icon={PeopleIcon}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Doctors"
            value={stats.totalDoctors}
            icon={DoctorIcon}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Patients"
            value={stats.totalPatients}
            icon={PatientIcon}
            color="info.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Appointments"
            value={stats.totalAppointments}
            icon={AppointmentIcon}
            color="warning.main"
          />
        </Grid>
      </Grid>

      <Typography variant="h5" gutterBottom>
        Quick Actions
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              User Management
            </Typography>
            <Typography color="text.secondary" paragraph>
              Manage system users, roles, and permissions.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => navigate('/admin/users')}
            >
              Manage Users
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Department Management
            </Typography>
            <Typography color="text.secondary" paragraph>
              Manage hospital departments and their details.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => navigate('/admin/departments')}
            >
              Manage Departments
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Reports
            </Typography>
            <Typography color="text.secondary" paragraph>
              View and generate system reports.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => navigate('/admin/reports')}
            >
              View Reports
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminDashboard; 