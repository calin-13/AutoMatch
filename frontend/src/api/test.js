import client from './client'

export const testApi = {
  async getQuestions(version = 2) {
    const { data } = await client.get(`/api/test/questions?version=${version}`)
    return data
  },
  async submit(version, answers) {
    const { data } = await client.post('/api/test/submit', { version, answers })
    return data
  },
}
