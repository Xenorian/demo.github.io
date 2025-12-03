import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

const REPO_NAME = 'demo.github.io';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  base: process.env.NODE_ENV === 'production' ? REPO_NAME : '/',
  server: {
    host: '0.0.0.0',
    port: 5173, // 可选，指定端口
    strictPort: true, // 可选，如果端口被占用则报错
  }
})
