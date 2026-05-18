import client from './client'

export const profileApi = {
  async get() {
    const { data } = await client.get('/api/auth/profile')
    return data
  },
  async update(updates) {
    const { data } = await client.put('/api/auth/profile', updates)
    return data
  },
}
