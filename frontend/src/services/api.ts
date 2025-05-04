// src/services/api.ts
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api", // certifique-se que o backend Flask está rodando nesta URL
});

export default api;