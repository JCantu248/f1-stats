const API_BASE_URL = 'http://localhost:8000/api'

async function apiRequest(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`)

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  return await response.json()
}

export function getRaces() {
  return apiRequest('/races/')
}

export function getRace(raceId) {
  return apiRequest(`/races/${raceId}/`)
}

export function getDrivers() {
  return apiRequest('/drivers/')
}

export function getDriver(driverNumber) {
  return apiRequest(`/drivers/${driverNumber}/`)
}

export function getConstructors() {
  return apiRequest('/constructors/')
}

export function getConstructor(constructorId) {
  return apiRequest(`/constructors/${constructorId}/`)
}

export function getDriverStandings() {
  return apiRequest('/standings/drivers/')
}

export function getConstructorStandings() {
  return apiRequest('/standings/constructors/')
}