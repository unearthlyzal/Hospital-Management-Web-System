import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import DrugSearch from '../../components/DrugSearch';
import { medicalRecords } from '../../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`medical-records-tabpanel-${index}`}
      aria-labelledby={`medical-records-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const MedicalRecords = () => {
  const [tabValue, setTabValue] = useState(0);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    try {
      const response = await medicalRecords.getAll();
      setRecords(response.data);
    } catch (err: any) {
      setError('Failed to fetch medical records');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleDrugSelect = (drug: any) => {
    // Handle drug selection, e.g., add to prescription
    console.log('Selected drug:', drug);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Medical Records
      </Typography>

      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="medical records tabs"
        >
          <Tab label="Records" />
          <Tab label="Medications" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {/* Existing medical records content */}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box>
            <Typography variant="h6" gutterBottom>
              Search Medications
            </Typography>
            <Typography color="text.secondary" paragraph>
              Search for medications to view detailed information, including indications,
              dosage, warnings, and interactions.
            </Typography>
            <Divider sx={{ my: 2 }} />
            <DrugSearch onDrugSelect={handleDrugSelect} />
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default MedicalRecords; 