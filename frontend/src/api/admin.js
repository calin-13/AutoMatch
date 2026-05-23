import client from './client'

export const adminApi = {
  async getStats() {
    const { data } = await client.get('/api/admin/stats')
    return data
  },
  async getMLMetrics() {
    const { data } = await client.get('/api/admin/ml/metrics')
    return data
  },
  async getFeatureImportance() {
    const { data } = await client.get('/api/admin/ml/feature-importance')
    return data
  },
  async getModelComparison() {
    const { data } = await client.get('/api/admin/ml/comparison')
    return data
  },
  async getUsers() {
    const { data } = await client.get('/api/admin/users')
    return data
  },
  async deleteUser(userId) {
    const { data } = await client.delete(`/api/admin/users/${userId}`)
    return data
  },
  async promoteUser(userId) {
    const { data } = await client.post(`/api/admin/promote/${userId}`)
    return data
  },
  async demoteUser(userId) {
    const { data } = await client.post(`/api/admin/demote/${userId}`)
    return data
  },
  async getRecentFeedback() {
    const { data } = await client.get('/api/admin/feedback/recent')
    return data
  },
}
