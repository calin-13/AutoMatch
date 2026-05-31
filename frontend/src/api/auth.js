import client from './client'

export const authApi = {
  async login(email, password) {
    const { data } = await client.post('/api/auth/login', { email, password })
    return data
  },
  async register(email, username, password) {
    const { data } = await client.post('/api/auth/register', { email, username, password })
    return data
  },
  async me() {
    const { data } = await client.get('/api/auth/me')
    return data
  },
  async forgotPassword(email) {
    const { data } = await client.post('/api/auth/forgot-password', { email })
    return data
  },
  async resetPassword(token, newPassword) {
    const { data } = await client.post('/api/auth/reset-password', { token, new_password: newPassword })
    return data
  },
}
