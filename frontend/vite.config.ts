/**
 * 文件名: vite.config.ts
 * 编辑时间: 2025-03-14
 * 代码编写人: Lambert tang
 * 描述: Vite 构建配置，代理 /api 到后端 8000 端口
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
