import api from './client'

export const incidentsAPI = {
  create: (data) => api.post('/incidents/', data),
  list: (params) => api.get('/incidents/', { params }),
  getStatus: (id) => api.get(`/incidents/${id}/status`),
  delete: (id) => api.delete(`/incidents/${id}`),
}
