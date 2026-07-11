import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite is the tool that runs our Vue app during development (with instant
// reload) and bundles it into static files for production.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
  },
})