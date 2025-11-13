import axios from 'axios'

// Auto-detect environment and set API URL
// IMPORTANT: Use 127.0.0.1 instead of localhost for Windows compatibility
const getApiBaseUrl = (): string => {
  // Priority 1: Use environment variable if set (Amplify production)
  // But replace localhost with 127.0.0.1 if present
  if (import.meta.env.VITE_API_BASE_URL) {
    const envUrl = import.meta.env.VITE_API_BASE_URL
    // Replace localhost with 127.0.0.1 for Windows compatibility
    return envUrl.replace('localhost', '127.0.0.1')
  }
  
  // Priority 2: Always use 127.0.0.1 for local development (Windows compatibility)
  // This ensures it works even if localhost DNS resolution fails
  return 'http://127.0.0.1:8000/api'
}

const API_BASE_URL = getApiBaseUrl()

// Log the API base URL for debugging
console.log('API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  // Don't set default Content-Type - let Axios auto-detect based on data type
  // FormData will get multipart/form-data, JSON will get application/json
})

export default api

