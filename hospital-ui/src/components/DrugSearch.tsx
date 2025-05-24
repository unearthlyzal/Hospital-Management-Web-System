import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Alert,
} from '@mui/material';
import { ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import SearchBar from './SearchBar';
import drugApi from '../services/drugApi';

interface DrugSearchProps {
  onDrugSelect?: (drug: any) => void;
}

const DrugSearch: React.FC<DrugSearchProps> = ({ onDrugSelect }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [selectedDrug, setSelectedDrug] = useState<any>(null);
  const [drugDetails, setDrugDetails] = useState<any>(null);

  const handleSearch = async (query: string) => {
    if (!query) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await drugApi.searchDrugs(query);
      setSearchResults(response.results);
    } catch (err: any) {
      setError('Failed to search drugs. Please try again.');
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDrugSelect = async (drug: any) => {
    setSelectedDrug(drug);
    if (onDrugSelect) {
      onDrugSelect(drug);
    }

    try {
      const details = await drugApi.getDrugDetails(drug.product_ndc);
      setDrugDetails(details.results[0]);
    } catch (err: any) {
      setError('Failed to fetch drug details.');
    }
  };

  return (
    <Box>
      <SearchBar
        onSearch={handleSearch}
        placeholder="Search for medications..."
        loading={loading}
      />

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      <Box mt={2}>
        {searchResults.map((drug) => (
          <Card
            key={drug.product_ndc}
            sx={{
              mb: 2,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => handleDrugSelect(drug)}
          >
            <CardContent>
              <Typography variant="h6">
                {drug.brand_name || drug.generic_name}
              </Typography>
              <Typography color="text.secondary">
                {drug.dosage_form} • {drug.route.join(', ')}
              </Typography>
              <Typography variant="body2">
                Manufacturer: {drug.labeler_name}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {drugDetails && (
        <Box mt={3}>
          <Typography variant="h5" gutterBottom>
            Detailed Information
          </Typography>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Indications and Usage</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                {drugDetails.indications_and_usage?.join('\n\n')}
              </Typography>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Dosage and Administration</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                {drugDetails.dosage_and_administration?.join('\n\n')}
              </Typography>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Warnings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                {drugDetails.warnings?.join('\n\n')}
              </Typography>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Drug Interactions</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                {drugDetails.drug_interactions?.join('\n\n')}
              </Typography>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Adverse Reactions</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                {drugDetails.adverse_reactions?.join('\n\n')}
              </Typography>
            </AccordionDetails>
          </Accordion>

          {drugDetails.boxed_warning && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Boxed Warning
              </Typography>
              {drugDetails.boxed_warning.map((warning: string, index: number) => (
                <Typography key={index} paragraph>
                  {warning}
                </Typography>
              ))}
            </Alert>
          )}
        </Box>
      )}
    </Box>
  );
};

export default DrugSearch; 