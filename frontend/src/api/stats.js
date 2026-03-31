import client from './client'

export function getOverview() {
  return client.get('/stats/overview')
}

export function getCategoryDistribution() {
  return client.get('/stats/category-distribution')
}

export function getNatureDistribution() {
  return client.get('/stats/nature-distribution')
}

export function getFlavorDistribution() {
  return client.get('/stats/flavor-distribution')
}
