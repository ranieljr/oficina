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
    host: true, // Equivalent to --host CLI flag
    port: 5174, // Specify the port to avoid conflicts if 5173 is used
    strictPort: true, // Ensure it uses port 5174
    hmr: {
        // Necessary for HMR through proxy
        clientPort: 5173
    },
    allowedHosts: ["http://127.0.0.1:5000/"]
  }
})

