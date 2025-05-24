import React, { useState } from 'react';
import { Box, TextField, MenuItem, Button } from '@mui/material';

interface FormData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  blood_group: string;
  phone: string;
  address: string;
}

const Profile: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: '',
    blood_group: '',
    phone: '',
    address: '',
  });

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    // Handle form submission
  };

  return (
    <Box
      component="main"
      sx={{
        maxWidth: 'lg',
        mx: 'auto',
        p: 3,
      }}
    >
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
        }}
      >
        <TextField
          fullWidth
          label="First Name"
          name="first_name"
          value={formData.first_name}
          onChange={handleInputChange}
          required
        />
        <TextField
          fullWidth
          label="Last Name"
          name="last_name"
          value={formData.last_name}
          onChange={handleInputChange}
          required
        />
        <TextField
          fullWidth
          label="Date of Birth"
          name="date_of_birth"
          type="date"
          value={formData.date_of_birth}
          onChange={handleInputChange}
          required
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          fullWidth
          select
          label="Gender"
          name="gender"
          value={formData.gender}
          onChange={handleInputChange}
          required
        >
          <MenuItem value="male">Male</MenuItem>
          <MenuItem value="female">Female</MenuItem>
        </TextField>
        <TextField
          fullWidth
          select
          label="Blood Group"
          name="blood_group"
          value={formData.blood_group}
          onChange={handleInputChange}
          required
        >
          <MenuItem value="A+">A+</MenuItem>
          <MenuItem value="A-">A-</MenuItem>
          <MenuItem value="B+">B+</MenuItem>
          <MenuItem value="B-">B-</MenuItem>
          <MenuItem value="AB+">AB+</MenuItem>
          <MenuItem value="AB-">AB-</MenuItem>
          <MenuItem value="O+">O+</MenuItem>
          <MenuItem value="O-">O-</MenuItem>
        </TextField>
        <TextField
          fullWidth
          label="Phone"
          name="phone"
          value={formData.phone}
          onChange={handleInputChange}
          required
        />
        <Box sx={{ gridColumn: '1 / -1' }}>
          <TextField
            fullWidth
            label="Address"
            name="address"
            value={formData.address}
            onChange={handleInputChange}
            required
            multiline
            rows={3}
          />
        </Box>
        <Box sx={{ gridColumn: '1 / -1' }}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
          >
            Update Profile
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default Profile; 