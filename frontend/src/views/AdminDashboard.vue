<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h3 class="mb-1">Admin Dashboard</h3>
        <p class="text-muted mb-0">Manage companies, review drives, and monitor placement activity.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

    <div class="row mb-4">
      <div class="col-md-3" v-for="(value, label) in statCards" :key="label">
        <div class="card text-center shadow-sm">
          <div class="card-body">
            <h6 class="text-muted">{{ label }}</h6>
            <h3>{{ value }}</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-6">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Registered Companies</h5>
            <div class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Contact</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="company in companies" :key="company.id">
                    <td>{{ company.company_name }}</td>
                    <td>{{ company.hr_contact || 'N/A' }}</td>
                    <td>
                      <span class="badge" :class="statusClass(company.approval_status)">{{ company.approval_status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Placement Drives</h5>
            <div class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead>
                  <tr>
                    <th>Drive</th>
                    <th>Company</th>
                    <th>Package</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="drive in drives" :key="drive.id">
                    <td>{{ drive.title }}</td>
                    <td>{{ drive.company }}</td>
                    <td>{{ drive.package || 'N/A' }}</td>
                    <td>
                      <span class="badge" :class="statusClass(drive.status)">{{ drive.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4 mt-1">
      <div class="col-lg-6">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Pending Company Requests</h5>
            <div v-if="pendingCompanies.length === 0" class="text-muted">None pending.</div>
            <div class="card mb-2" v-for="c in pendingCompanies" :key="c.id">
              <div class="card-body d-flex justify-content-between align-items-center">
                <span>{{ c.company_name }} ({{ c.hr_contact }})</span>
                <div>
                  <button class="btn btn-sm btn-success me-1" @click="approveCompany(c.id)">Approve</button>
                  <button class="btn btn-sm btn-danger" @click="rejectCompany(c.id)">Reject</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Pending Drives</h5>
            <div v-if="pendingDrives.length === 0" class="text-muted">None pending.</div>
            <div class="card mb-2" v-for="d in pendingDrives" :key="d.id">
              <div class="card-body d-flex justify-content-between align-items-center">
                <span>{{ d.title }} — {{ d.company }} ({{ d.package }})</span>
                <div>
                  <button class="btn btn-sm btn-success me-1" @click="approveDrive(d.id)">Approve</button>
                  <button class="btn btn-sm btn-danger" @click="rejectDrive(d.id)">Reject</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiRequest } from '../api'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'AdminDashboard',
  setup() {
    const auth = useAuthStore()
    return { auth }
  },
  data() {
    return {
      stats: { total_students: 0, total_companies: 0, total_drives: 0, total_selected: 0 },
      companies: [],
      drives: [],
      pendingCompanies: [],
      pendingDrives: [],
      errorMessage: '',
    }
  },
  computed: {
    statCards() {
      return {
        'Total Students': this.stats.total_students,
        'Total Companies': this.stats.total_companies,
        'Total Drives': this.stats.total_drives,
        'Total Selected': this.stats.total_selected,
      }
    },
  },
  async mounted() {
    await Promise.all([
      this.loadStats(),
      this.loadCompanies(),
      this.loadDrives(),
      this.loadPendingCompanies(),
      this.loadPendingDrives(),
    ])
  },
  methods: {
    statusClass(status) {
      const map = {
        approved: 'bg-success',
        pending: 'bg-warning text-dark',
        rejected: 'bg-danger',
      }
      return map[status] || 'bg-secondary'
    },
    async loadStats() {
      try {
        this.stats = await apiRequest('/drives/stats', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async loadCompanies() {
      try {
        this.companies = await apiRequest('/companies/all', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async loadDrives() {
      try {
        const active = await apiRequest('/drives/active', { token: this.auth.token })
        const past = await apiRequest('/drives/past', { token: this.auth.token })
        this.drives = [...active, ...past].map((drive) => ({
          ...drive,
          status: drive.approval_status || (drive.created_at ? 'active' : 'past'),
        }))
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async loadPendingCompanies() {
      try {
        this.pendingCompanies = await apiRequest('/companies/pending', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async loadPendingDrives() {
      try {
        this.pendingDrives = await apiRequest('/drives/pending', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async approveCompany(id) {
      await apiRequest(`/companies/${id}/approve`, { method: 'POST', token: this.auth.token })
      await this.loadCompanies()
      await this.loadPendingCompanies()
    },
    async rejectCompany(id) {
      await apiRequest(`/companies/${id}/reject`, { method: 'POST', token: this.auth.token })
      await this.loadCompanies()
      await this.loadPendingCompanies()
    },
    async approveDrive(id) {
      await apiRequest(`/drives/${id}/approve`, { method: 'POST', token: this.auth.token })
      await this.loadDrives()
      await this.loadPendingDrives()
    },
    async rejectDrive(id) {
      await apiRequest(`/drives/${id}/reject`, { method: 'POST', token: this.auth.token })
      await this.loadDrives()
      await this.loadPendingDrives()
    },
  },
}
</script>
