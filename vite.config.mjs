import { defineConfig } from 'vite';
export default defineConfig({base:'./',build:{outDir:'dist',assetsDir:'assets',sourcemap:false,emptyOutDir:true},esbuild:{jsx:'transform',jsxFactory:'React.createElement'}});
