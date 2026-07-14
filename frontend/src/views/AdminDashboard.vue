<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h3 class="mb-1">Admin Dashboard</h3>
        <p class="text-muted mb-0">Manage companies, review drives, and monitor placement activity.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

    <!-- Tab Navigation -->
    <ul class="nav nav-tabs my-3">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'overview' }" href="#" @click.prevent="activeTab = 'overview'">
          Overview
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'companies' }" href="#" @click.prevent="activeTab = 'companies'">
          Companies
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'drives' }" href="#" @click.prevent="activeTab = 'drives'">
          Drives
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'students' }" href="#" @click.prevent="activeTab = 'students'">
          Students
        </a>
      </li>
    </ul>

    <!-- Overview Tab -->
    <div v-if="activeTab === 'overview'">
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
      <p class="text-muted mt-4">Use the Companies and Drives tabs to manage registrations and approvals.</p>
    </div>

    <!-- Companies Tab -->
    <div v-if="activeTab === 'companies'">
      <div class="row g-4">
        <div class="col-lg-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="card-title mb-0">All Registered Companies</h5>
                <div class="d-flex gap-2">
                  <input v-model="companySearch" class="form-control" style="min-width: 240px;" placeholder="Search companies" @keyup.enter="searchCompanies" />
                  <button class="btn btn-outline-primary" @click="searchCompanies">Search</button>
                  <button class="btn btn-outline-secondary" @click="resetCompanySearch">Reset</button>
                </div>
              </div>
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Contact</th>
                      <th>Industry</th>
                      <th>Approval</th>
                      <th>Account</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="company in companies" :key="company.id">
                      <td>{{ company.company_name }}</td>
                      <td>{{ company.hr_contact || 'N/A' }}</td>
                      <td>{{ company.industry || 'N/A' }}</td>
                      <td>
                        <span class="badge" :class="statusClass(company.approval_status)">{{ company.approval_status }}</span>
                      </td>
                      <td>
                        <span class="badge" :class="company.is_active ? 'bg-success' : 'bg-secondary'">{{ company.is_active ? 'Active' : 'Inactive' }}</span>
                      </td>
                      <td>
                        <button class="btn btn-sm" :class="company.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleCompanyStatus(company.id)">
                          {{ company.is_active ? 'Deactivate' : 'Activate' }}
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p v-if="companies.length === 0" class="text-muted mt-3">No companies registered yet.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mt-3">
        <div class="col-lg-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="card-title">Pending Company Requests</h5>
              <div v-if="pendingCompanies.length === 0" class="text-muted">None pending.</div>
              <div class="card mb-2" v-for="c in pendingCompanies" :key="c.id">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 class="mb-1">{{ c.company_name }}</h6>
                      <small class="text-muted">{{ c.hr_contact }}</small>
                    </div>
                    <div>
                      <button class="btn btn-sm btn-success me-2" @click="approveCompany(c.id)">Approve</button>
                      <button class="btn btn-sm btn-danger" @click="rejectCompany(c.id)">Reject</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Drives Tab -->
    <div v-if="activeTab === 'drives'">
      <div class="row g-4">
        <div class="col-lg-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="card-title">All Placement Drives</h5>
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Drive</th>
                      <th>Company</th>
                      <th>Package</th>
                      <th>Location</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="drive in drives" :key="drive.id">
                      <td>{{ drive.title }}</td>
                      <td>{{ drive.company }}</td>
                      <td>{{ drive.package || 'N/A' }}</td>
                      <td>{{ drive.location || 'N/A' }}</td>
                      <td>
                        <span class="badge" :class="statusClass(drive.status)">{{ drive.status }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p v-if="drives.length === 0" class="text-muted mt-3">No drives available.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mt-3">
        <div class="col-lg-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="card-title">Pending Drive Approvals</h5>
              <div v-if="pendingDrives.length === 0" class="text-muted">None pending.</div>
              <div class="card mb-2" v-for="d in pendingDrives" :key="d.id">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 class="mb-1">{{ d.title }}</h6>
                      <small class="text-muted">{{ d.company }} • {{ d.package || 'Package TBD' }} • {{ d.location || 'Location TBD' }}</small>
                    </div>
                    <div>
                      <button class="btn btn-sm btn-success me-2" @click="approveDrive(d.id)">Approve</button>
                      <button class="btn btn-sm btn-danger" @click="rejectDrive(d.id)">Reject</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Students Tab -->
    <div v-if="activeTab === 'students'">
      <div class="row g-4">
        <div class="col-lg-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="card-title mb-0">All Registered Students</h5>
                <div class="d-flex gap-2">
                  <input v-model="studentSearch" class="form-control" style="min-width: 240px;" placeholder="Search students" @keyup.enter="searchStudents" />
                  <button class="btn btn-outline-primary" @click="searchStudents">Search</button>
                  <button class="btn btn-outline-secondary" @click="resetStudentSearch">Reset</button>
                </div>
              </div>
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Branch</th>
                      <th>Year</th>
                      <th>CGPA</th>
                      <th>Skills</th>
                      <th>Account</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="student in students" :key="student.id">
                      <td>{{ student.name }}</td>
                      <td>{{ student.branch || 'N/A' }}</td>
                      <td>{{ student.year || 'N/A' }}</td>
                      <td>{{ student.cgpa || 'N/A' }}</td>
                      <td>{{ student.skills || 'N/A' }}</td>
                      <td>
                        <span class="badge" :class="student.is_active ? 'bg-success' : 'bg-secondary'">{{ student.is_active ? 'Active' : 'Inactive' }}</span>
                      </td>
                      <td>
                        <button class="btn btn-sm" :class="student.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleStudentStatus(student.id)">
                          {{ student.is_active ? 'Deactivate' : 'Activate' }}
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p v-if="students.length === 0" class="text-muted mt-3">No students registered yet.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mt-3">
        <div class="col-lg-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="card-title">All Student Applications</h5>
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Drive</th>
                      <th>Company</th>
                      <th>Status</th>
                      <th>Applied On</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="application in applications" :key="application.id">
                      <td>{{ application.student_name }}</td>
                      <td>{{ application.drive_title }}</td>
                      <td>{{ application.company }}</td>
                      <td>
                        <span class="badge" :class="statusClass(application.status)">{{ application.status }}</span>
                      </td>
                      <td>{{ application.applied_on }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p v-if="applications.length === 0" class="text-muted mt-3">No applications submitted yet.</p>
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
      activeTab: 'overview',
      stats: { total_students: 0, total_companies: 0, total_drives: 0, total_selected: 0 },
      companies: [],
      drives: [],
      students: [],
      applications: [],
      pendingCompanies: [],
      pendingDrives: [],
      companySearch: '',
      studentSearch: '',
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
      this.loadStudents(),
      this.loadAllApplications(),
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
    async loadStudents() {
      try {
        this.students = await apiRequest('/students/search?q=', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async loadAllApplications() {
      try {
        this.applications = await apiRequest('/students/applications/all', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async searchCompanies() {
      const query = this.companySearch.trim()
      if (!query) {
        await this.loadCompanies()
        return
      }
      try {
        this.companies = await apiRequest(`/companies/search?q=${encodeURIComponent(query)}`, { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async resetCompanySearch() {
      this.companySearch = ''
      await this.loadCompanies()
    },
    async searchStudents() {
      const query = this.studentSearch.trim()
      if (!query) {
        await this.loadStudents()
        return
      }
      try {
        this.students = await apiRequest(`/students/search?q=${encodeURIComponent(query)}`, { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async resetStudentSearch() {
      this.studentSearch = ''
      await this.loadStudents()
    },
    async toggleCompanyStatus(id) {
      try {
        await apiRequest(`/companies/${id}/toggle-active`, { method: 'POST', token: this.auth.token })
        await this.loadCompanies()
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async toggleStudentStatus(id) {
      try {
        await apiRequest(`/students/${id}/toggle-active`, { method: 'POST', token: this.auth.token })
        await this.loadStudents()
      } catch (err) {
        this.errorMessage = err.message
      }
    },
  },
}
</script>
