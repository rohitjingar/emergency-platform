import api from './client'

export const volunteersAPI = {
  getProfile: () => api.get('/volunteers/me'),
  register: (data) => api.post('/volunteers/register', data),
  updateProfile: (data) => api.patch('/volunteers/profile', data),
  updateLocation: (data) => api.patch('/volunteers/location', data),
  updateStatus: (data) => api.patch('/volunteers/status', data),
  getAvailable: (params) => api.get('/volunteers/available', { params }),
  getPending: () => api.get('/volunteers/my-pending'),
  acceptIncident: (id) => api.post(`/volunteers/incidents/${id}/accept`),
  declineIncident: (id, data) => api.post(`/volunteers/incidents/${id}/decline`, data),
}
