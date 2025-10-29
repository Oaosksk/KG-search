import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const authAPI = {
  googleLogin: (token) => api.post('/auth/google', { token })
}

export const uploadAPI = {
  uploadFile: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export const searchAPI = {
  search: (query, top_k = 10) => api.post('/search/', { query, top_k }),
  submitFeedback: (data) => api.post('/search/feedback', data)
}

export const filesAPI = {
  listFiles: () => api.get('/files/list'),
  getFileKG: (fileId) => api.get(`/files/kg/${fileId}`),
  deleteFile: (fileId) => api.delete(`/delete/file/${fileId}`)
}

export const syncAPI = {
  syncGoogleDrive: () => api.post('/sync/gdrive'),
  getSyncStatus: () => api.get('/sync/status'),
  processGDriveFile: (fileId) => api.post(`/sync/process/${fileId}`)
}

export default api
