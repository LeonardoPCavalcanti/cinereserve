import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Deploy em GitHub Pages sob https://<user>.github.io/cinereserve/
export default defineConfig({
  plugins: [react()],
  base: '/cinereserve/',
});
