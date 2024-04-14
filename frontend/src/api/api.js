import axios from 'axios';

// Set up the base URL for all Axios requests
const API_BASE_URL = VITE_API_URLcl; // Change this to the actual URL of your Django backend

// Axios instance to set default properties
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  // If you have additional headers, set them here
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

// Functions for making API calls
const api = {
  // Sign up a new user
  signUp(userData) {
    return apiClient.post('accounts/signup/', userData);
  },
  // Log in a user
  signIn(credentials) {
    return apiClient.post('signin/', credentials);
  },
  // Add more API calls as needed
};

export default api;
