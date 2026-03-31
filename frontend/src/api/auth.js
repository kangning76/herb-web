import client from './client'

export function login(username, password) {
  return client.post('/auth/login', { username, password })
}

export function refreshToken(refresh_token) {
  return client.post('/auth/refresh', { refresh_token })
}

export function getMe() {
  return client.get('/auth/me')
}
