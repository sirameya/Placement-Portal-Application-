<template>
  <div class="container mt-4">
    <h3>Student Dashboard</h3>
    <p v-if="studentCgpa !== null" class="text-muted">Your CGPA: <strong>{{ studentCgpa }}</strong></p>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Total Applications</h5>
            <p class="display-6 text-primary">{{ applications.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Shortlisted</h5>
            <p class="display-6 text-warning">{{ shortlistedCount }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title">Selected</h5>
            <p class="display-6 text-success">{{ selectedCount }}</p>
          </div>
        </div>
      </div>
    </div>

    <ul class="nav nav-tabs my-3">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'browse' }" href="#" @click.prevent="activeTab = 'browse'">
          Browse Drives
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'applied' }" href="#" @click.prevent="activeTab = 'applied'">
          Applied Drives
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'applications' }" href="#" @click.prevent="activeTab = 'applications'">
          All Applications
        </a>
      </li>
    </ul>

    <!-- Browse & apply tab -->
    <div v-if="activeTab === 'browse'">
      <!-- Sub-tabs for eligible vs all drives -->
      <ul class="nav nav-tabs mb-3 ms-3">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: browseSubTab === 'eligible' }" href="#" @click.prevent="browseSubTab = 'eligible'">
            Eligible Drives
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: browseSubTab === 'all' }" href="#" @click.prevent="browseSubTab = 'all'">
            All Drives
          </a>
        </li>
      </ul>

      <!-- Eligible drives (matching CGPA) -->
      <div v-if="browseSubTab === 'eligible'">
        <p v-if="eligibleDrives.length === 0" class="text-muted">No eligible drives available for you right now.</p>
        <DriveCard
          v-for="drive in eligibleDrives"
          :key="drive.id"
          :drive="drive"
          :isApplied="isDriveApplied(drive)"
          @apply="handleApply"
        />
      </div>

      <!-- All drives -->
      <div v-if="browseSubTab === 'all'">
        <p v-if="drives.length === 0" class="text-muted">No approved drives available right now.</p>
        <DriveCard
          v-for="drive in drives"
          :key="drive.id"
          :drive="drive"
          :isApplied="isDriveApplied(drive)"
          @apply="handleApply"
        />
      </div>
    </div>

    <!-- Applied Drives tab -->
    <div v-if="activeTab === 'applied'">
      <p v-if="appliedDrives.length === 0" class="text-muted">You haven't applied to any drives yet.</p>
      <div class="row">
        <div v-for="drive in appliedDrives" :key="drive.id" class="col-md-6 mb-3">
          <div class="card h-100">
            <div class="card-body">
              <h5 class="card-title">{{ drive.title }}</h5>
              <p class="card-text">
                <strong>Company:</strong> {{ drive.company }}<br>
                <strong>Package:</strong> {{ drive.package }}<br>
                <strong>Status:</strong> 
                <span class="badge" :class="getStatusBadgeClass(drive.status)">{{ drive.status }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Application history tab -->
    <div v-if="activeTab === 'applications'">
      <table class="table">
        <thead>
          <tr><th>Drive</th><th>Company</th><th>Applied On</th><th>Status</th></tr>
        </thead>
        <tbody>
          <ApplicationRow v-for="app in applications" :key="app.application_id" :application="app" />
        </tbody>
      </table>
      <p v-if="applications.length === 0" class="text-muted">You haven't applied to anything yet.</p>
    </div>
  </div>
</template>

<script>
import { apiRequest } from '../api'
import { useAuthStore } from '../stores/auth'
import DriveCard from '../components/DriveCard.vue'
import ApplicationRow from '../components/ApplicationRow.vue'

export default {
  name: 'StudentDashboard',
  components: { DriveCard, ApplicationRow },
  setup() {
    const auth = useAuthStore()
    return { auth }
  },
  data() {
    return {
      activeTab: 'browse',
      browseSubTab: 'eligible',
      drives: [],
      applications: [],
      studentCgpa: null,
      errorMessage: '',
    }
  },
  computed: {
    eligibleDrives() {
      // Filter drives where student's CGPA meets the minimum requirement
      if (this.studentCgpa === null) return this.drives
      return this.drives.filter(drive => this.studentCgpa >= drive.min_cgpa)
    },
    appliedDrives() {
      // Get the drives that the student has applied to
      const appliedDriveIds = new Set(this.applications.map(app => {
        // Find the corresponding drive by title and company
        const drive = this.drives.find(d => d.title === app.drive_title && d.company === app.company)
        return drive ? drive.id : null
      }))
      
      return Array.from(appliedDriveIds)
        .filter(id => id !== null)
        .map(driveId => {
          const drive = this.drives.find(d => d.id === driveId)
          const appData = this.applications.find(a => a.drive_title === drive.title && a.company === drive.company)
          return {
            ...drive,
            status: appData.status
          }
        })
    },
    shortlistedCount() {
      return this.applications.filter(app => app.status === 'shortlisted').length
    },
    selectedCount() {
      return this.applications.filter(app => app.status === 'selected').length
    }
  },
  // `mounted()` runs once, right after this component first appears on
  // screen — the natural place to fetch initial data.
  async mounted() {
    await this.loadStudentProfile()
    await this.loadDrives()
    await this.loadApplications()
  },
  methods: {
    async loadStudentProfile() {
      try {
        const profile = await apiRequest('/students/profile', { token: this.auth.token })
        this.studentCgpa = profile.cgpa
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async loadDrives() {
      try {
        this.drives = await apiRequest('/students/drives', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async loadApplications() {
      try {
        this.applications = await apiRequest('/students/applications', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async handleApply(driveId) {
      try {
        await apiRequest(`/students/drives/${driveId}/apply`, {
          method: 'POST',
          token: this.auth.token,
        })
        // Refresh applications so the new one shows up immediately
        await this.loadApplications()
        this.activeTab = 'applications'
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    getStatusBadgeClass(status) {
      switch (status) {
        case 'selected':
          return 'bg-success'
        case 'shortlisted':
          return 'bg-warning text-dark'
        case 'rejected':
          return 'bg-danger'
        case 'applied':
        default:
          return 'bg-secondary'
      }
    },
    isDriveApplied(drive) {
      // Check if the current drive has been applied to
      return this.applications.some(app => app.drive_title === drive.title && app.company === drive.company)
    },
  },
}
</script>
