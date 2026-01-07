import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const legalAPI = {
  // Health check
  healthCheck: async () => {
    const response = await axios.get(`${API_BASE_URL}/`);
    return response.data;
  },

  // Query the legal assistant
  queryLegalAssistant: async (question, chatHistory = []) => {
    const response = await axios.post(`${API_BASE_URL}/query`, {
      question,
      chat_history: chatHistory
    });
    return response.data;
  },

  // Get legal sources
  getLegalSources: async () => {
    const response = await axios.get(`${API_BASE_URL}/legal-sources`);
    return response.data;
  },

  // Reload documents
  reloadDocuments: async () => {
    const response = await axios.post(`${API_BASE_URL}/reload-documents`);
    return response.data;
  }
};

export default legalAPI;
