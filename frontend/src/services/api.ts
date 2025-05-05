// src/api.ts
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL 
  ?? 'https://lauf-backend.onrender.com';

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});