import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // 这里的 '/api' 对应你代码里的相对路径开头
      '/api': {
        target: 'http://127.0.0.1:8000', // 你的后端地址
        changeOrigin: true,
        // 如果后端接口本身没有 /api 前缀，需要重写路径
        // rewrite: (path) => path.replace(/^\/api/, '') 
      }
    }
  }
})