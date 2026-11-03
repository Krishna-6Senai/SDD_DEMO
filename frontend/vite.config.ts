import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    // Spring Boot serves this from the classpath; the Dockerfile copies dist into
    // src/main/resources/static.
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    // Local development only. In the container there is one origin, so no proxy and no CORS.
    proxy: {
      '/api': 'http://localhost:8080',
    },
  },
});
