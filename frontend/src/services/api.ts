import axios from "axios";

// Backend base URL via .env
export const API_BASE = import.meta.env.VITE_API_URL;

// Endpoints centralizados
export const ENDPOINTS = {
  login: `${API_BASE}/api/auth/login`,
  maquinas: `${API_BASE}/api/maquinas`,
  manutencoes: `${API_BASE}/api/manutencoes`,
  exportExcel: `${API_BASE}/export/manutencoes/excel`,
  exportPDF: `${API_BASE}/export/manutencoes/pdf`,
};

// Instância Axios com baseURL
const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // se necessário para cookies/autenticação
});

export { api };