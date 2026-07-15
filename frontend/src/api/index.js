/**
 * api/index.js — every component talks to Flask through this ONE
 * function, instead of writing fetch() + headers + error-handling
 * from scratch in every .vue file.
 */

const BASE_URL = "http://localhost:5000/api"

export async function apiRequest(path, { method = "GET", body = null, token = null } = {}) {
  const headers = { "Content-Type": "application/json" }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  })

  // Try to parse JSON; if the response isn't JSON (HTML error page),
  // fall back to text so the frontend can show a readable message.
  const contentType = response.headers.get('content-type') || ''
  let data = null
  if (contentType.includes('application/json')) {
    try {
      data = await response.json()
    } catch (e) {
      // malformed JSON
      const txt = await response.text()
      throw new Error(`Invalid JSON response: ${txt.slice(0, 200)}`)
    }
  } else {
    // not JSON (could be HTML error page like an auth redirect)
    const txt = await response.text()
    if (!response.ok) {
      // Provide status and first part of body to help debugging
      const summary = txt ? txt.replace(/\s+/g, ' ').slice(0, 400) : response.statusText
      throw new Error(`HTTP ${response.status}: ${summary}`)
    }
    // If it is OK but not JSON, still return the raw text
    return txt
  }

  if (!response.ok) {
    throw new Error(data && (data.error || data.message) ? (data.error || data.message) : `HTTP ${response.status}`)
  }

  return data
}

export async function searchDrives(query = '') {
  return apiRequest(`/drives/search?q=${encodeURIComponent(query)}`)
}

export async function getReports() {
  return apiRequest('/drives/reports')
}

export async function getNotificationStatus() {
  return apiRequest('/drives/notifications/status')
}
