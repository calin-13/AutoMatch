import client from './client'

export const carsApi = {
  async getById(id) {
    const { data } = await client.get(`/api/cars/${id}`)
    return data
  },
  async list(params = {}) {
    const { data } = await client.get('/api/cars', { params })
    return data
  },
  async search(filters = {}) {
    const { data } = await client.get('/api/cars/search', { params: filters })
    return data
  },
}
