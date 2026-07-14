<template>
  <div class="container mt-5" style="max-width: 450px;">
    <h3 class="mb-4">Register</h3>

    <form ref="registerForm" @submit.prevent="handleRegister">
      <div class="mb-3">
        <label class="form-label">I am a...</label>
        <select v-model="role" class="form-select">
          <option value="student">Student</option>
          <option value="company">Company</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="email" type="email" class="form-control" required autocomplete="email" />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-control" required minlength="6" />
      </div>

      <!-- Only shown when registering as a student -->
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Full Name</label>
        <input v-model="name" type="text" class="form-control" required minlength="2" />
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Branch</label>
        <select v-model="branch" class="form-select" required>
          <option value="">-- Select Branch --</option>
          <option value="CSE">Computer Science Engineering (CSE)</option>
          <option value="ECE">Electronics & Communication (ECE)</option>
          <option value="EEE">Electrical Engineering (EEE)</option>
          <option value="ME">Mechanical Engineering (ME)</option>
          <option value="CE">Civil Engineering (CE)</option>
          <option value="IT">Information Technology (IT)</option>
          <option value="BME">Biomedical Engineering (BME)</option>
        </select>
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Year</label>
        <input v-model.number="year" type="number" min="1" max="8" class="form-control" placeholder="e.g., 4" />
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">CGPA</label>
        <input v-model.number="cgpa" type="number" step="0.01" min="0" max="10" class="form-control" placeholder="e.g., 8.5" />
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Phone</label>
        <input v-model="phone" type="text" class="form-control" placeholder="e.g., +91 9876543210" />
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Address</label>
        <input v-model="address" type="text" class="form-control" placeholder="Current address" />
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Portfolio URL</label>
        <input v-model="portfolioUrl" type="url" class="form-control" placeholder="https://..." />
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Skill 1</label>
        <select v-model="skill1" class="form-select" required>
          <option value="">-- Select Skill --</option>
          <option value="Python">Python</option>
          <option value="Java">Java</option>
          <option value="JavaScript">JavaScript</option>
          <option value="C++">C++</option>
          <option value="C#">C#</option>
          <option value="React">React</option>
          <option value="Angular">Angular</option>
          <option value="Vue.js">Vue.js</option>
          <option value="Node.js">Node.js</option>
          <option value="Django">Django</option>
          <option value="Spring Boot">Spring Boot</option>
          <option value="SQL">SQL</option>
          <option value="MongoDB">MongoDB</option>
          <option value="AWS">AWS</option>
          <option value="Docker">Docker</option>
          <option value="Kubernetes">Kubernetes</option>
          <option value="Git">Git</option>
          <option value="REST APIs">REST APIs</option>
          <option value="GraphQL">GraphQL</option>
          <option value="Machine Learning">Machine Learning</option>
        </select>
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Skill 2</label>
        <select v-model="skill2" class="form-select" required>
          <option value="">-- Select Skill --</option>
          <option value="Python">Python</option>
          <option value="Java">Java</option>
          <option value="JavaScript">JavaScript</option>
          <option value="C++">C++</option>
          <option value="C#">C#</option>
          <option value="React">React</option>
          <option value="Angular">Angular</option>
          <option value="Vue.js">Vue.js</option>
          <option value="Node.js">Node.js</option>
          <option value="Django">Django</option>
          <option value="Spring Boot">Spring Boot</option>
          <option value="SQL">SQL</option>
          <option value="MongoDB">MongoDB</option>
          <option value="AWS">AWS</option>
          <option value="Docker">Docker</option>
          <option value="Kubernetes">Kubernetes</option>
          <option value="Git">Git</option>
          <option value="REST APIs">REST APIs</option>
          <option value="GraphQL">GraphQL</option>
          <option value="Machine Learning">Machine Learning</option>
        </select>
      </div>
      <div v-if="role === 'student'" class="mb-3">
        <label class="form-label">Skill 3</label>
        <select v-model="skill3" class="form-select" required>
          <option value="">-- Select Skill --</option>
          <option value="Python">Python</option>
          <option value="Java">Java</option>
          <option value="JavaScript">JavaScript</option>
          <option value="C++">C++</option>
          <option value="C#">C#</option>
          <option value="React">React</option>
          <option value="Angular">Angular</option>
          <option value="Vue.js">Vue.js</option>
          <option value="Node.js">Node.js</option>
          <option value="Django">Django</option>
          <option value="Spring Boot">Spring Boot</option>
          <option value="SQL">SQL</option>
          <option value="MongoDB">MongoDB</option>
          <option value="AWS">AWS</option>
          <option value="Docker">Docker</option>
          <option value="Kubernetes">Kubernetes</option>
          <option value="Git">Git</option>
          <option value="REST APIs">REST APIs</option>
          <option value="GraphQL">GraphQL</option>
          <option value="Machine Learning">Machine Learning</option>
        </select>
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
        <div class="mb-3">
          <label class="form-label">Industry</label>
          <input v-model="industry" type="text" class="form-control" placeholder="e.g., IT / Manufacturing" />
        </div>
        <div class="mb-3">
          <label class="form-label">Address</label>
          <input v-model="address" type="text" class="form-control" placeholder="Office address" />
        </div>
        <div class="mb-3">
          <label class="form-label">Contact Email</label>
          <input v-model="contactEmail" type="email" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Phone Number</label>
          <input v-model="phoneNumber" type="text" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Description</label>
          <textarea v-model="description" class="form-control" rows="3"></textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">Employee Count</label>
          <input v-model.number="employeeCount" type="number" min="1" class="form-control" />
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
      phone: '',
      address: '',
      portfolioUrl: '',
      skill1: '',
      skill2: '',
      skill3: '',
      companyName: '',
      hrContact: '',
      website: '',
      industry: '',
      contactEmail: '',
      phoneNumber: '',
      description: '',
      employeeCount: null,
      errorMessage: '',
      successMessage: '',
      loading: false,
    }
  },
  methods: {
    validateForm() {
      const form = this.$refs.registerForm
      if (form && !form.checkValidity()) {
        form.reportValidity()
        return false
      }
      return true
    },
    async handleRegister() {
      if (!this.validateForm()) {
        return
      }
      this.errorMessage = ''
      this.successMessage = ''
      this.loading = true

      // Build the request body differently depending on role —
      // the backend expects different fields for each.
      const body = { email: this.email, password: this.password, role: this.role }
      if (this.role === 'student') {
        body.name = this.name
        if (this.cgpa !== null && this.cgpa !== '') body.cgpa = this.cgpa
        if (this.branch) body.branch = this.branch
        if (this.year) body.year = this.year
        if (this.phone) body.phone = this.phone
        if (this.address) body.address = this.address
        if (this.portfolioUrl) body.portfolio_url = this.portfolioUrl
        // Combine 3 selected skills into comma-separated string
        if (this.skill1 || this.skill2 || this.skill3) {
          const skills = [this.skill1, this.skill2, this.skill3].filter(s => s).join(', ')
          body.skills = skills
        }
      } else {
        body.company_name = this.companyName
        body.hr_contact = this.hrContact
        body.website = this.website
        if (this.industry) body.industry = this.industry
        if (this.address) body.address = this.address
        if (this.contactEmail) body.contact_email = this.contactEmail
        if (this.phoneNumber) body.phone_number = this.phoneNumber
        if (this.description) body.description = this.description
        if (this.employeeCount !== null && this.employeeCount !== '') body.employee_count = this.employeeCount
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
