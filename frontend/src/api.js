const BASE = '/api'

export function getToken() {
  return localStorage.getItem('token')
}

export function setToken(token) {
  localStorage.setItem('token', token)
}

export function clearToken() {
  localStorage.removeItem('token')
}

async function request(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (res.status === 401) {
    clearToken()
    window.location.href = '/'
    throw new Error('Session expired')
  }
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail.detail || `Request failed (${res.status})`)
  }
  return res.status === 204 ? null : res.json()
}

export const api = {
  register: (phone, name, address) =>
    request('/auth/register', { method: 'POST', body: { phone, name, address } }),
  login: (phone) => request('/auth/login', { method: 'POST', body: { phone } }),
  me: () => request('/users/me'),
  chat: (message) => request('/chat', { method: 'POST', body: { message } }),
  history: () => request('/chat/history'),
  clearHistory: () => request('/chat/history', { method: 'DELETE' }),
  pendingOrders: () => request('/chat/orders/pending'),
  confirmOrder: (id, confirmed) =>
    request(`/chat/orders/${id}/confirm`, { method: 'POST', body: { confirmed } }),
  preferences: () => request('/users/me/preferences'),
  updatePreferences: (prefs) => request('/users/me/preferences', { method: 'PUT', body: prefs }),
  menu: () => request('/menu'),
  favorites: () => request('/users/me/favorites'),
  addFavorite: (id) => request(`/users/me/favorites/${id}`, { method: 'POST' }),
  removeFavorite: (id) => request(`/users/me/favorites/${id}`, { method: 'DELETE' }),
  traces: (limit = 20) => request(`/telemetry/traces?limit=${limit}`),
  clearTraces: () => request('/telemetry/traces/clear', { method: 'POST' }),
  prompts: () => request('/telemetry/prompts'),
  activatePrompt: (version) => request('/telemetry/prompts/activate', { method: 'POST', body: { version } }),
  createPrompt: (payload) => request('/telemetry/prompts', { method: 'POST', body: payload }),
  models: () => request('/telemetry/models'),
  evalDataset: () => request('/telemetry/evals/dataset'),
  addEvalItem: (payload) => request('/telemetry/evals/dataset/items', { method: 'POST', body: payload }),
  deleteEvalItem: (id) => request(`/telemetry/evals/dataset/items/${id}`, { method: 'DELETE' }),
  runBenchmark: (promptVersion, modelName) => request('/telemetry/evals/run', { method: 'POST', body: { prompt_version: promptVersion, model_name: modelName } }),
  latestBenchmark: () => request('/telemetry/evals/latest'),
}

