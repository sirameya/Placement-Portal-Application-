<template>
  <div class="app-shell">
    <nav class="topbar">
      <div class="brand-wrap">
        <div class="brand-badge">P</div>
        <div>
          <h4>Placement Portal</h4>
          <p>Campus hiring made simple</p>
        </div>
      </div>
      <div v-if="auth.isLoggedIn" class="user-actions">
        <span class="role-pill">{{ auth.role }}</span>
        <button class="ghost-btn" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <main class="page-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  setup() {
    const auth = useAuthStore()
    return { auth }
  },
  methods: {
    handleLogout() {
      this.auth.logout()
      this.$router.push('/login')
    },
  },
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: linear-gradient(135deg, #f4f7ff 0%, #eef4ff 100%);
  color: #11213a;
}
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(255,255,255,0.95);
  box-shadow: 0 8px 30px rgba(17,33,58,0.08);
}
.brand-wrap {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}
.brand-badge {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
  font-weight: 700;
  font-size: 1.1rem;
}
.brand-wrap h4 {
  margin: 0;
  font-size: 1.1rem;
}
.brand-wrap p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}
.user-actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.role-pill {
  padding: 0.45rem 0.8rem;
  border-radius: 999px;
  background: #e8f0ff;
  color: #1d4ed8;
  font-weight: 600;
  text-transform: capitalize;
}
.ghost-btn {
  border: none;
  border-radius: 10px;
  padding: 0.55rem 0.9rem;
  background: #111827;
  color: white;
  cursor: pointer;
}
.page-content {
  padding: 1.5rem 2rem 2.5rem;
}
</style>
