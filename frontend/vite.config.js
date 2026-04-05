import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/incidents': 'http://localhost:8000',
      '/volunteers': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
      '/notifications': 'http://localhost:8000',
      '/system': 'http://localhost:8000',
      '/ai': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    }
  }
})
