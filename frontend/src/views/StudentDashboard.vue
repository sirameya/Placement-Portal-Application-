<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="mb-1">Student Dashboard</h3>
        <p v-if="studentName" class="text-muted mb-0">Welcome, <strong>{{ studentName }}</strong>! Browse drives and track your applications.</p>
        <p v-if="studentCgpa !== null" class="text-muted mb-0">Your CGPA: <strong>{{ studentCgpa }}</strong></p>
      </div>
    </div>

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
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'profile' }" href="#" @click.prevent="activeTab = 'profile'">
          Profile
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
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h5 class="card-title">Active Applications</h5>
          <div class="table-responsive">
            <table class="table mb-0">
              <thead>
                <tr><th>Drive</th><th>Company</th><th>Applied On</th><th>Status</th></tr>
              </thead>
              <tbody>
                <ApplicationRow v-for="app in activeApplications" :key="app.application_id" :application="app" />
              </tbody>
            </table>
          </div>
          <p v-if="activeApplications.length === 0" class="text-muted mt-3 mb-0">You don't have any active applications right now.</p>
        </div>
      </div>

      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h5 class="card-title">Placement History</h5>
          <div class="table-responsive">
            <table class="table mb-0">
              <thead>
                <tr><th>Drive</th><th>Company</th><th>Applied On</th><th>Status</th></tr>
              </thead>
              <tbody>
                <ApplicationRow v-for="app in placementHistory" :key="app.application_id" :application="app" />
              </tbody>
            </table>
          </div>
          <p v-if="placementHistory.length === 0" class="text-muted mt-3 mb-0">No past placement history yet.</p>
        </div>
      </div>

      <div class="card shadow-sm">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h5 class="card-title mb-0">Export Applications</h5>
            <button class="btn btn-outline-primary btn-sm" @click="exportApplications" :disabled="exporting">
              {{ exporting ? 'Preparing export...' : 'Export as CSV' }}
            </button>
          </div>
          <p class="text-muted mb-3">Export your applications as a CSV file. The export runs in the background and you’ll get a download link once it is ready.</p>
          <div v-if="exportMessage" class="alert alert-success">{{ exportMessage }}</div>
          <div v-if="exportError" class="alert alert-danger">{{ exportError }}</div>
          <div v-if="exportFileName" class="mt-2">
            <a :href="`/api/students/exports/${exportFileName}`" target="_blank" class="btn btn-success btn-sm">Download CSV</a>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile tab -->
    <div v-if="activeTab === 'profile'">
      <div class="row">
        <div class="col-md-6">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="card-title">Edit Profile</h5>
              <div v-if="profileSaveSuccess" class="alert alert-success">{{ profileSaveSuccess }}</div>
              <div v-if="profileSaveError" class="alert alert-danger">{{ profileSaveError }}</div>

              <div class="mb-3">
                <label class="form-label">Name</label>
                <input v-model="profileForm.name" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Branch</label>
                <input v-model="profileForm.branch" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Year</label>
                <input v-model.number="profileForm.year" type="number" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">CGPA</label>
                <input v-model.number="profileForm.cgpa" type="number" step="0.01" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Skills</label>
                <input v-model="profileForm.skills" class="form-control" placeholder="e.g. Python, SQL, React" />
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input v-model="profileForm.phone" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Address</label>
                <input v-model="profileForm.address" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Portfolio URL</label>
                <input v-model="profileForm.portfolio_url" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">LinkedIn URL</label>
                <input v-model="profileForm.linkedin_url" class="form-control" />
              </div>

              <button class="btn btn-primary" @click="saveProfile" :disabled="savingProfile">
                {{ savingProfile ? 'Saving...' : 'Save Profile' }}
              </button>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="card-title">Resume Upload</h5>
              <p class="text-muted">Upload your resume (PDF) to be visible to companies reviewing your applications.</p>
              
              <div v-if="resumeUploadSuccess" class="alert alert-success">{{ resumeUploadSuccess }}</div>
              <div v-if="resumeUploadError" class="alert alert-danger">{{ resumeUploadError }}</div>

              <div class="mb-3">
                <label class="form-label">Select Resume (PDF)</label>
                <input 
                  ref="resumeInput"
                  type="file" 
                  class="form-control" 
                  accept=".pdf" 
                  @change="handleResumeFileSelect"
                  aria-label="Select resume file"
                />
              </div>

              <button 
                class="btn btn-primary" 
                @click="handleResumeUpload"
                :disabled="!selectedResumeFile || uploading"
              >
                {{ uploading ? 'Uploading...' : 'Upload Resume' }}
              </button>

              <div v-if="studentResumePath" class="mt-3">
                <p class="text-success"><i class="bi bi-check-circle"></i> Resume uploaded</p>
                <small class="text-muted">{{ studentResumePath }}</small>
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
      studentName: '',
      studentCgpa: null,
      studentBranch: '',
      studentYear: '',
      studentSkills: '',
      studentResumePath: '',
      profileForm: {
        name: '',
        cgpa: null,
        branch: '',
        year: '',
        skills: '',
        phone: '',
        address: '',
        portfolio_url: '',
        linkedin_url: '',
      },
      drives: [],
      applications: [],
      errorMessage: '',
      selectedResumeFile: null,
      uploading: false,
      savingProfile: false,
      profileSaveSuccess: '',
      profileSaveError: '',
      resumeUploadSuccess: '',
      resumeUploadError: '',
      exporting: false,
      exportMessage: '',
      exportError: '',
      exportFileName: '',
      exportTaskId: '',
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
    },
    activeApplications() {
      return this.applications.filter(app => app.status === 'applied')
    },
    placementHistory() {
      return this.applications.filter(app => ['shortlisted', 'selected', 'rejected'].includes(app.status))
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
        this.studentName = profile.name
        this.studentCgpa = profile.cgpa
        this.studentBranch = profile.branch || ''
        this.studentYear = profile.year || ''
        this.studentSkills = profile.skills || ''
        this.studentResumePath = profile.resume_path || ''
        this.profileForm = {
          name: profile.name || '',
          cgpa: profile.cgpa ?? null,
          branch: profile.branch || '',
          year: profile.year || '',
          skills: profile.skills || '',
          phone: profile.phone || '',
          address: profile.address || '',
          portfolio_url: profile.portfolio_url || '',
          linkedin_url: profile.linkedin_url || '',
        }
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
    async exportApplications() {
      this.exporting = true
      this.exportError = ''
      this.exportMessage = ''
      this.exportFileName = ''

      try {
        const result = await apiRequest('/students/applications/export', {
          method: 'POST',
          token: this.auth.token,
        })
        this.exportTaskId = result.task_id
        this.exportMessage = 'Export started. Please wait while your CSV is being prepared.'
        this.pollExportStatus(result.task_id)
      } catch (err) {
        this.exportError = err.message || 'Export could not be started.'
        this.exporting = false
      }
    },
    async pollExportStatus(taskId) {
      try {
        const status = await apiRequest(`/students/exports/status/${taskId}`, { token: this.auth.token })
        if (status.state === 'SUCCESS') {
          const resultPath = status.result || ''
          const fileName = resultPath.split(/[\\/]/).pop()
          this.exportFileName = fileName
          this.exportMessage = 'Your export is ready.'
          this.exporting = false
          return
        }
        if (status.state === 'FAILURE') {
          this.exportError = 'The export job failed.'
          this.exporting = false
          return
        }
        setTimeout(() => this.pollExportStatus(taskId), 2000)
      } catch (err) {
        this.exportError = err.message || 'Could not check export status.'
        this.exporting = false
      }
    },
    async saveProfile() {
      this.savingProfile = true
      this.profileSaveSuccess = ''
      this.profileSaveError = ''

      try {
        const payload = {
          ...this.profileForm,
          cgpa: this.profileForm.cgpa === '' || this.profileForm.cgpa === null ? null : this.profileForm.cgpa,
        }
        await apiRequest('/students/profile', {
          method: 'PATCH',
          token: this.auth.token,
          body: payload,
        })
        this.profileSaveSuccess = 'Profile updated successfully.'
        await this.loadStudentProfile()
      } catch (err) {
        this.profileSaveError = err.message || 'Failed to update profile'
      } finally {
        this.savingProfile = false
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
    handleResumeFileSelect(event) {
      const file = event.target.files[0]
      if (file && file.type === 'application/pdf') {
        this.selectedResumeFile = file
        this.resumeUploadError = ''
      } else if (file) {
        this.resumeUploadError = 'Please select a valid PDF file'
        this.selectedResumeFile = null
      }
    },
    async handleResumeUpload() {
      if (!this.selectedResumeFile) return

      this.uploading = true
      this.resumeUploadSuccess = ''
      this.resumeUploadError = ''

      try {
        const formData = new FormData()
        formData.append('resume', this.selectedResumeFile)

        // Custom upload using fetch (FormData not supported by apiRequest helper)
        const response = await fetch('/api/students/profile/upload_resume', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.auth.token}`,
          },
          body: formData,
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.error || 'Upload failed')
        }

        const result = await response.json()
        this.resumeUploadSuccess = 'Resume uploaded successfully!'
        this.studentResumePath = result.resume_path
        this.selectedResumeFile = null
        this.$refs.resumeInput.value = ''
      } catch (err) {
        this.resumeUploadError = err.message || 'Failed to upload resume'
      } finally {
        this.uploading = false
      }
    },
  },
}
</script>
