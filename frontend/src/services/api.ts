// src/services/api.ts
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://lauf-backend.onrender.com'
});

export default api;