import api from './client'

export const notificationsAPI = {
  getMy: (params) => api.get('/notifications/my', { params }),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
}
