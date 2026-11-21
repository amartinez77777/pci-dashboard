import {defineConfig} from 'vite';

// Relative asset paths are required for HTTPS static hosting under a subdirectory
// (for example GitHub Pages /project-name/). Hash routes need no rewrite server.
export default defineConfig({base:'./',build:{outDir:'dist',assetsDir:'assets'}});
