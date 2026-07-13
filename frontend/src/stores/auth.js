/**
 * stores/auth.js — Pinia store holding login state.
 *
 * Why do we need this instead of each component managing its own
 * "am I logged in?" variable? Because MANY components need to know
 * the current user's role (NavBar shows different links, router
 * blocks pages, dashboards fetch role-specific data). A store is a
 * single source of truth all of them read from.
 *
 * defineStore(id, { state, actions }) — this is the "Options API"
 * style of Pinia, matching the Options API style we're using in
 * our .vue components.
 */

import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // We initialize from localStorage so refreshing the page doesn't
    // log the user out — the token survives a page reload.
    token: localStorage.getItem('token') || null,
    role: localStorage.getItem('role') || null,
    userId: localStorage.getItem('userId') || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    /**
     * Called after a successful /api/auth/login response.
     * Saves to BOTH Pinia state (so the app reacts instantly) AND
     * localStorage (so it survives a page refresh).
     */
    setSession({ access_token, role, user_id }) {
      this.token = access_token
      this.role = role
      this.userId = user_id

      localStorage.setItem('token', access_token)
      localStorage.setItem('role', role)
      localStorage.setItem('userId', user_id)
    },

    logout() {
      this.token = null
      this.role = null
      this.userId = null

      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('userId')
    },
  },
})
