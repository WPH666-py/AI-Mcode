import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 3020,
    strictPort: true,
    proxy: {
      '/api': 'http://127.0.0.1:3018',
      '/ws': {
        target: 'ws://127.0.0.1:3031',
        ws: true,
      },
      '/media': 'http://127.0.0.1:3018',
    },
  },
})
