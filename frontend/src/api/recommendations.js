import client from './client'

export const recommendationsApi = {
  async getFromProfile(diversity = false) {
    const url = diversity
      ? '/api/recommend-from-profile?diversity=true'
      : '/api/recommend-from-profile'
    const { data } = await client.post(url)
    return data
  },
}
