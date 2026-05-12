import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Unwrap DRF error shapes: { error: ... } → throw with message
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const data = error.response?.data
    const message =
      typeof data?.error === 'string'
        ? data.error
        : typeof data?.error === 'object'
        ? Object.values(data.error).flat().join(' ')
        : error.message
    return Promise.reject(new Error(message))
  }
)

export default client