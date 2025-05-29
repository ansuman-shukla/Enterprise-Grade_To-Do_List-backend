import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Unable to connect to server. Please check if the backend is running.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

// Task API functions
export const taskAPI = {
  // Parse natural language input and create task
  parseTask: async (text) => {
    try {
      const response = await api.post('/tasks/parse', { text });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get all tasks
  getAllTasks: async () => {
    try {
      const response = await api.get('/tasks/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get task by ID
  getTask: async (taskId) => {
    try {
      const response = await api.get(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update task
  updateTask: async (taskId, updateData) => {
    try {
      const response = await api.put(`/tasks/${taskId}`, updateData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete task
  deleteTask: async (taskId) => {
    try {
      const response = await api.delete(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

// Health check function
export const healthCheck = async () => {
  try {
    const response = await axios.get('http://localhost:8000/health');
    return response.data;
  } catch (error) {
    throw new Error('Backend server is not responding');
  }
};

export default api;
