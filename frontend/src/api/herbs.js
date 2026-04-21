import client from './client'

export function getHerbs(params = {}) {
  return client.get('/herbs', { params })
}

export function getHerb(id) {
  return client.get(`/herbs/${id}`)
}

export function getCategories() {
  return client.get('/herbs/categories')
}

export function createHerb(data) {
  return client.post('/herbs', data)
}

export function updateHerb(id, data) {
  return client.put(`/herbs/${id}`, data)
}

export function deleteHerb(id) {
  return client.delete(`/herbs/${id}`)
}

export function uploadHerbImage(id, file) {
  const formData = new FormData()
  formData.append('file', file)
  return client.post(`/herbs/${id}/image`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function importHerbsCsv(file) {
  const formData = new FormData()
  formData.append('file', file)
  return client.post('/herbs/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getHerbRecommendations(id, params = {}) {
  return client.get(`/herbs/${id}/recommendations`, { params })
}

export function exploreRecommendations(params = {}) {
  return client.get('/herbs/recommendations/explore', { params })
}
