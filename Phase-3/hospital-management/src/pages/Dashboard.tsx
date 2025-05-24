import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.first_name} {user?.last_name}
      </Typography>
      
      <Box sx={{ 
        display: 'grid',
        gap: 3,
        gridTemplateColumns: {
          xs: '1fr',
          md: '1fr 1fr',
          lg: '1fr 1fr 1fr'
        }
      }}>
        <Paper
          sx={{
            p: 3,
            display: 'flex',
            flexDirection: 'column',
            height: 240,
          }}
        >
          <Typography variant="h6" gutterBottom>
            Recent Appointments
          </Typography>
          {/* Add appointment list here */}
        </Paper>
        
        <Paper
          sx={{
            p: 3,
            display: 'flex',
            flexDirection: 'column',
            height: 240,
          }}
        >
          <Typography variant="h6" gutterBottom>
            Medical Records
          </Typography>
          {/* Add medical records summary here */}
        </Paper>
        
        <Paper
          sx={{
            p: 3,
            display: 'flex',
            flexDirection: 'column',
            height: 240,
          }}
        >
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          {/* Add quick action buttons here */}
        </Paper>
      </Box>
    </Box>
  );
};

export default Dashboard; 