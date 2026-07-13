<template>
  <div class="container mt-5" style="max-width: 450px;">
    <h3 class="mb-4">Register</h3>

    <form @submit.prevent="handleRegister">
      <div class="mb-3">
        <label class="form-label">I am a...</label>
        <select v-model="role" class="form-select">
          <option value="student">Student</option>
          <option value="company">Company</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>

      <!-- Only shown when registering as a student -->
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Full Name</label>
        <input v-model="name" type="text" class="form-control" required />
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Branch</label>
        <input v-model="branch" type="text" class="form-control" placeholder="e.g., Computer Science" />
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Year</label>
        <input v-model.number="year" type="number" min="1" max="8" class="form-control" placeholder="e.g., 4" />
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">CGPA</label>
        <input v-model.number="cgpa" type="number" step="0.01" min="0" max="10" class="form-control" placeholder="e.g., 8.5" />
      </div>

      <!-- Only shown when registering as a company -->
      <template v-else>
        <div class="mb-3">
          <label class="form-label">Company Name</label>
          <input v-model="companyName" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">HR Contact</label>
          <input v-model="hrContact" type="text" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Website</label>
          <input v-model="website" type="url" class="form-control" />
        </div>
      </template>

      <div v-if="errorMessage" class="alert alert-danger py-2">{{ errorMessage }}</div>
      <div v-if="successMessage" class="alert alert-success py-2">{{ successMessage }}</div>

      <button type="submit" class="btn btn-primary w-100" :disabled="loading">
        {{ loading ? 'Registering...' : 'Register' }}
      </button>
    </form>

    <p class="mt-3 text-center">
      Already have an account? <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script>
import { apiRequest } from '../api'

export default {
  name: 'RegisterView',
  data() {
    return {
      role: 'student',
      email: '',
      password: '',
      name: '',
      cgpa: null,
        branch: '',
        year: null,
      companyName: '',
      hrContact: '',
      website: '',
      errorMessage: '',
      successMessage: '',
      loading: false,
    }
  },
  methods: {
    async handleRegister() {
      this.errorMessage = ''
      this.successMessage = ''
      this.loading = true

      // Build the request body differently depending on role —
      // the backend expects different fields for each.
      const body = { email: this.email, password: this.password, role: this.role }
      if (this.role === 'student') {
        body.name = this.name
        if (this.cgpa) body.cgpa = this.cgpa
        if (this.branch) body.branch = this.branch
        if (this.year) body.year = this.year
      } else {
        body.company_name = this.companyName
        body.hr_contact = this.hrContact
        body.website = this.website
      }

      try {
        const result = await apiRequest('/auth/register', { method: 'POST', body })
        this.successMessage = result.message
        setTimeout(() => this.$router.push('/login'), 1500)
      } catch (err) {
        this.errorMessage = err.message
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
