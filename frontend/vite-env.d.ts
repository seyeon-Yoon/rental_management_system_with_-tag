/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  // 더 많은 환경 변수들을 여기에 추가...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}