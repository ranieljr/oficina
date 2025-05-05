// src/services/api.ts
export const API_BASE = 'https://lauf-backend.onrender.com';

export const ENDPOINTS = {
  login: `${API_BASE}/api/auth/login`,
  maquinas: `${API_BASE}/api/maquinas`,
  manutencoes: `${API_BASE}/api/manutencoes`,
  exportExcel: `${API_BASE}/api/export/manutencoes/excel`,
  exportPDF: `${API_BASE}/api/export/manutencoes/pdf`,
};