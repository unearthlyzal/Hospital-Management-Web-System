import React, { useState } from 'react';
import { Grid, TextField, FormControl, InputLabel, Select, MenuItem, Button } from '@mui/material';

const Profile: React.FC = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    department_id: '',
    specialization: '',
    qualification: '',
    experience_years: '',
  });

  const [departments, setDepartments] = useState([]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFormData({ ...formData, [name]: value });
  };

  return (
    <Grid container spacing={2}>
      <Grid component="div" item xs={12} sm={6}>
        <TextField
          fullWidth
          label="First Name"
          name="first_name"
          value={formData.first_name || ''}
          onChange={handleInputChange}
          required
        />
      </Grid>
      <Grid component="div" item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Last Name"
          name="last_name"
          value={formData.last_name || ''}
          onChange={handleInputChange}
          required
        />
      </Grid>
      <Grid component="div" item xs={12} sm={6}>
        <FormControl fullWidth>
          <InputLabel>Department</InputLabel>
          <Select
            name="department_id"
            value={formData.department_id || ''}
            onChange={handleInputChange}
            label="Department"
            required
          >
            {departments.map((dept) => (
              <MenuItem key={dept.id} value={dept.id}>
                {dept.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid component="div" item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Specialization"
          name="specialization"
          value={formData.specialization || ''}
          onChange={handleInputChange}
          required
        />
      </Grid>
      <Grid component="div" item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Qualification"
          name="qualification"
          value={formData.qualification || ''}
          onChange={handleInputChange}
          required
        />
      </Grid>
      <Grid component="div" item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Years of Experience"
          name="experience_years"
          type="number"
          value={formData.experience_years || ''}
          onChange={handleInputChange}
          required
          inputProps={{ min: 0 }}
        />
      </Grid>
      <Grid component="div" item xs={12}>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          size="large"
          fullWidth
        >
          Update Profile
        </Button>
      </Grid>
    </Grid>
  );
};

export default Profile; 