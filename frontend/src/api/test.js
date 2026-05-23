import client from './client'

export const testApi = {
  async getQuestions(version) {
    const params = {}
    if (version != null) params.version = version
    const { data } = await client.get('/api/test/questions', { params })
    return data
  },

  async submit(version, answers) {
    const { data } = await client.post('/api/test/submit', { version, answers })
    return data
  },

  async getMyResponses() {
    const { data } = await client.get('/api/test/my-responses')
    return data
  },
}
