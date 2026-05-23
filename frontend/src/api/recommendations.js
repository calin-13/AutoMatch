import client from './client'

export const recommendationsApi = {
  async getFromProfile(diversity = false) {
    const url = diversity
      ? '/api/recommend-from-profile?diversity=true'
      : '/api/recommend-from-profile'
    const { data } = await client.post(url)
    return data
  },
  async getHistory() {
    const { data } = await client.get('/api/auth/recommendations')
    return data
  },
  async getHistoryById(id) {
    const { data } = await client.get(`/api/auth/recommendations/${id}`)
    return data
  },
  async submitSessionFeedback(recId, rating, comment = null) {
    const payload = { rating }
    if (comment) payload.comment = comment
    const { data } = await client.post(`/api/recommendations/${recId}/feedback`, payload)
    return data
  },
}
