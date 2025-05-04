// src/services/api.ts
import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'https://lauf-backend.onrender.com'
});

export default api;