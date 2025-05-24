import axios from 'axios';

const FDA_API_BASE_URL = 'https://api.fda.gov/drug';
const API_KEY = process.env.REACT_APP_FDA_API_KEY || '';

interface DrugSearchResponse {
  meta: {
    disclaimer: string;
    terms: string;
    license: string;
    last_updated: string;
    results: {
      skip: number;
      limit: number;
      total: number;
    };
  };
  results: Array<{
    product_ndc: string;
    generic_name: string;
    brand_name: string;
    labeler_name: string;
    dosage_form: string;
    route: string[];
    active_ingredients: Array<{
      name: string;
      strength: string;
    }>;
  }>;
}

interface DrugLabelResponse {
  meta: {
    disclaimer: string;
    terms: string;
    license: string;
    last_updated: string;
  };
  results: Array<{
    effective_time: string;
    warnings: string[];
    dosage_and_administration: string[];
    indications_and_usage: string[];
    contraindications: string[];
    drug_interactions: string[];
    adverse_reactions: string[];
    boxed_warning?: string[];
  }>;
}

const drugApi = {
  /**
   * Search for drugs by name (brand or generic)
   */
  searchDrugs: async (query: string, limit: number = 10) => {
    try {
      const response = await axios.get<DrugSearchResponse>(
        `${FDA_API_BASE_URL}/ndc.json`,
        {
          params: {
            api_key: API_KEY,
            search: `(generic_name:"${query}" OR brand_name:"${query}")`,
            limit,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error searching drugs:', error);
      throw error;
    }
  },

  /**
   * Get detailed drug information by NDC code
   */
  getDrugDetails: async (ndcCode: string) => {
    try {
      const response = await axios.get<DrugLabelResponse>(
        `${FDA_API_BASE_URL}/label.json`,
        {
          params: {
            api_key: API_KEY,
            search: `product_ndc:"${ndcCode}"`,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching drug details:', error);
      throw error;
    }
  },

  /**
   * Search for drug interactions
   */
  searchInteractions: async (drugNames: string[]) => {
    try {
      const searchQuery = drugNames
        .map(name => `drug_interactions:"${name}"`)
        .join('+AND+');
      
      const response = await axios.get<DrugLabelResponse>(
        `${FDA_API_BASE_URL}/label.json`,
        {
          params: {
            api_key: API_KEY,
            search: searchQuery,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error searching drug interactions:', error);
      throw error;
    }
  },

  /**
   * Search for drug adverse effects
   */
  searchAdverseEffects: async (drugName: string) => {
    try {
      const response = await axios.get<DrugLabelResponse>(
        `${FDA_API_BASE_URL}/label.json`,
        {
          params: {
            api_key: API_KEY,
            search: `brand_name:"${drugName}" AND adverse_reactions:[*]`,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error searching adverse effects:', error);
      throw error;
    }
  },
};

export default drugApi; 