import api from './client'

export const systemAPI = {
  health: () => api.get('/system/health'),
  circuitBreaker: () => api.get('/system/circuit-breaker'),
  resetCircuit: () => api.post('/system/circuit-breaker/reset'),
  queues: () => api.get('/system/queues'),
}
