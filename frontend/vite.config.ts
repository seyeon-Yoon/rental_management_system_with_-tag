import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // 개발 서버 설정
  server: {
    port: 3000,
    host: true,
    open: false,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
      },
    },
  },

  // 빌드 설정
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          mui: ['@mui/material', '@mui/icons-material', '@emotion/react', '@emotion/styled'],
          router: ['react-router-dom'],
          query: ['@tanstack/react-query'],
          axios: ['axios'],
          utils: ['dayjs']
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith('.css')) {
            return 'assets/css/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        }
      },
    },
    // 빌드 성능 최적화
    target: 'es2020',
    chunkSizeWarningLimit: 1000,
  },

  // TypeScript path mapping 설정
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@/components': resolve(__dirname, './src/components'),
      '@/pages': resolve(__dirname, './src/pages'),
      '@/services': resolve(__dirname, './src/services'),
      '@/types': resolve(__dirname, './src/types'),
      '@/utils': resolve(__dirname, './src/utils'),
      '@/hooks': resolve(__dirname, './src/hooks'),
      '@/contexts': resolve(__dirname, './src/contexts'),
    },
  },

  // 환경 변수 접두사 설정
  envPrefix: 'VITE_',

  // 최적화 설정
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react/jsx-runtime',
      '@mui/material',
      '@mui/icons-material',
      '@emotion/react',
      '@emotion/styled',
      'react-router-dom',
      '@tanstack/react-query',
      'axios',
      'dayjs'
    ],
    exclude: ['@vite/client'],
  },

  // CSS 설정
  css: {
    devSourcemap: true,
    preprocessorOptions: {
      css: {
        charset: false,
      },
    },
  },

  // 미리보기 서버 설정
  preview: {
    port: 4173,
    host: true,
  },
})