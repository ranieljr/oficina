import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 5174,
    strictPort: true,
    hmr: {
      clientPort: 5174, // igual à porta do Vite
    },
    proxy: {
      "/api": {
        target: "https://lauf-backend.onrender.com",
        changeOrigin: true,
        secure: false,
      },
      "/export": {                    // <— proxy para /export também
        target: "https://lauf-backend.onrender.com",
        changeOrigin: true,
        secure: false,
        // (opcional) se quiser reescrever a URL,
        // mas aqui não é necessário, pois /export já bate
      },
    },
  },
});
