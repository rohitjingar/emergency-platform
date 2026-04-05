import api from './client'

export const adminAPI = {
  getReviewQueue: () => api.get('/admin/review-queue'),
  approveIncident: (id) => api.patch(`/admin/review-queue/${id}/approve`),
  overrideIncident: (id, data) => api.patch(`/admin/review-queue/${id}/override`, data),
  getStats: () => api.get('/admin/review-queue/stats'),
}
