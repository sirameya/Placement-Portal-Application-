<template>
  <div class="auth-layout">
    <section class="hero-card">
      <div class="hero-copy">
        <p class="eyebrow">Placement Platform</p>
        <h1>Connect students, companies, and recruiters in one place.</h1>
        <p class="subtext">Track opportunities, apply faster, and manage hiring pipelines effortlessly.</p>
        <div class="hero-highlights">
          <span>Live drives</span>
          <span>Resume tracking</span>
          <span>Admin approvals</span>
        </div>
      </div>

      <div class="form-card">
        <h3>Welcome back</h3>
        <p class="form-subtext">Sign in to continue your hiring journey.</p>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" type="email" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" required />
          </div>

          <div v-if="errorMessage" class="alert alert-danger py-2">{{ errorMessage }}</div>

          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>

        <p class="mt-3 text-center small-text">
          No account? <router-link to="/register">Register here</router-link>
        </p>
      </div>
    </section>
  </div>
</template>

<script>
import { apiRequest } from '../api'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'LoginView',
  setup() {
    const auth = useAuthStore()
    return { auth }
  },
  data() {
    return {
      email: '',
      password: '',
      errorMessage: '',
      loading: false,
    }
  },
  methods: {
    async handleLogin() {
      this.errorMessage = ''
      this.loading = true
      try {
        const result = await apiRequest('/auth/login', {
          method: 'POST',
          body: { email: this.email, password: this.password },
        })
        this.auth.setSession(result)
        this.$router.push(`/${result.role}`)
      } catch (err) {
        this.errorMessage = err.message
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.auth-layout {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}
.hero-card {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 1.5rem;
  width: min(1100px, 100%);
  background: white;
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
}
.hero-copy {
  padding: 1rem 0.5rem;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.25em;
  color: #2563eb;
  font-weight: 700;
  font-size: 0.8rem;
}
.hero-copy h1 {
  font-size: 2rem;
  line-height: 1.2;
  margin: 0.4rem 0 0.8rem;
}
.subtext {
  color: #64748b;
  font-size: 1rem;
}
.hero-highlights {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  margin-top: 1rem;
}
.hero-highlights span {
  background: #eff6ff;
  color: #1d4ed8;
  padding: 0.45rem 0.7rem;
  border-radius: 999px;
  font-size: 0.9rem;
}
.form-card {
  background: linear-gradient(135deg, #f8fbff, #eef5ff);
  border-radius: 18px;
  padding: 1.4rem;
}
.form-subtext {
  color: #64748b;
  font-size: 0.95rem;
}
.small-text {
  color: #64748b;
}
@media (max-width: 900px) {
  .hero-card {
    grid-template-columns: 1fr;
  }
}
</style>
