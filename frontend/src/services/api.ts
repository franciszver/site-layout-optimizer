import axios from 'axios'

// Auto-detect environment and set API URL
const getApiBaseUrl = (): string => {
  // Priority 1: Use environment variable if set (Amplify production)
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  
  // Priority 2: Check if running locally (development mode)
  if (import.meta.env.DEV || 
      window.location.hostname === 'localhost' || 
      window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000/api'
  }
  
  // Priority 3: Fallback to localhost for safety
  return 'http://localhost:8000/api'
}

const API_BASE_URL = getApiBaseUrl()

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api

