import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The dev server proxies /api to the FastAPI backend.
const backend = process.env.BACKEND_URL ?? 'http://localhost:8765'

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': backend } },
})
