import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // This allows us to access VITE_ variables inside this config file.
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    server: {
      // Required for Docker: Allows the server to be accessible outside the container
      host: true,
      port: 5173,
      
      // The Proxy logic
      proxy: {
        // Intercept any request starting with "/api"
        '/api': {
          // target will be "http://backend:8000" in Docker mode 
          // or empty/unused in local native mode
          target: env.VITE_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          // Strip "/api" from the URL before sending to FastAPI
          // e.g. /api/video/stream -> /video/stream
          rewrite: (path) => path.replace(/^\/api/, ''),
          // Enable websocket proxying (good for HMR and potential future features)
          ws: true,
        },
      },
    },
  }
})