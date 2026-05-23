import client from './client'

export const feedbackApi = {
  async submit(carId, rating, recommendationId = null, comment = null) {
    const payload = { car_id: carId, rating }
    if (recommendationId != null) payload.recommendation_id = recommendationId
    if (comment) payload.comment = comment
    const { data } = await client.post('/api/feedback', payload)
    return data
  },

  async getHistory() {
    const { data } = await client.get('/api/auth/feedback')
    return data
  },

  async getSummary() {
    const { data } = await client.get('/api/feedback/stats')
    return data
  },
}
