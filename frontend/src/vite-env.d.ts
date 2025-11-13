/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_MAPBOX_TOKEN: string
  readonly DEV: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

