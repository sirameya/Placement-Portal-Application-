<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="mb-1">Company Dashboard</h3>
        <p v-if="companyName" class="text-muted mb-0">Welcome, <strong>{{ companyName }}</strong>! Manage your placement drives and review applicants.</p>
      </div>
    </div>
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <h5 class="card-title">Company Details</h5>
        <div class="row g-3">
          <div class="col-md-6">
            <p class="mb-2"><strong>Company Name:</strong> {{ companyDetails.company_name || 'N/A' }}</p>
            <p class="mb-2"><strong>HR Contact:</strong> {{ companyDetails.hr_contact || 'N/A' }}</p>
            <p class="mb-2"><strong>Website:</strong> {{ companyDetails.website || 'N/A' }}</p>
            <p class="mb-2"><strong>Industry:</strong> {{ companyDetails.industry || 'N/A' }}</p>
            <p class="mb-2"><strong>Address:</strong> {{ companyDetails.address || 'N/A' }}</p>
          </div>
          <div class="col-md-6">
            <p class="mb-2"><strong>Contact Email:</strong> {{ companyDetails.contact_email || 'N/A' }}</p>
            <p class="mb-2"><strong>Phone Number:</strong> {{ companyDetails.phone_number || 'N/A' }}</p>
            <p class="mb-2"><strong>Employee Count:</strong> {{ companyDetails.employee_count || 'N/A' }}</p>
            <p class="mb-2"><strong>Approval Status:</strong> <span class="badge" :class="statusClass(companyDetails.approval_status)">{{ companyDetails.approval_status || 'N/A' }}</span></p>
            <p class="mb-2"><strong>Description:</strong> {{ companyDetails.description || 'N/A' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create a new drive -->
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Create New Drive</h5>
        
        <form @submit.prevent="handleCreateDrive" class="card p-3 shadow-sm">
          <div class="d-flex align-items-center justify-content-between mb-2">
            <div>
              <h5 class="mb-0">Create New Drive</h5>
              <small class="text-muted">Keep it short and attractive — students notice clear titles.</small>
            </div>
            <button type="button" class="btn btn-outline-secondary btn-sm" @click="showAdvanced = !showAdvanced">
              {{ showAdvanced ? 'Hide Advanced' : 'Advanced options' }}
            </button>
          </div>

          <div class="row g-2 mb-2">
            <div class="col-12">
              <label class="form-label">Job Title</label>
              <input v-model="newDrive.title" class="form-control form-control-lg" placeholder="Job title (e.g., Software Engineer - Intern)" required aria-label="Job Title" minlength="3" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Package</label>
              <input v-model="newDrive.salary_package" class="form-control" placeholder="Package (e.g., 6 LPA)" aria-label="Package" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Location</label>
              <input v-model="newDrive.location" class="form-control" placeholder="Location (City or Remote)" aria-label="Location" required />
            </div>
            <div class="col-md-4">
              <label class="form-label">Min CGPA</label>
              <input v-model.number="newDrive.min_cgpa" class="form-control" placeholder="Min CGPA (optional)" aria-label="Minimum CGPA" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Application Deadline</label>
              <input v-model="newDrive.application_deadline" type="datetime-local" class="form-control" aria-label="Application Deadline" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Drive / Interview Date</label>
              <input v-model="newDrive.drive_date" type="datetime-local" class="form-control" aria-label="Drive Date" />
            </div>
          </div>

          <transition name="fade">
            <div v-if="showAdvanced" class="border rounded p-3 bg-light">
              <div class="mb-2">
                <label class="form-label">Short Description</label>
                <textarea v-model="newDrive.description" class="form-control" rows="3" placeholder="Short description for students (what makes this role exciting?)" aria-label="Description"></textarea>
              </div>
              <div class="row g-2">
                <div class="col-md-6">
                  <label class="form-label">Skills Required</label>
                  <input v-model="newDrive.skills_required" class="form-control" placeholder="Skills required (comma-separated)" aria-label="Skills Required" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Eligible Branches</label>
                  <input v-model="newDrive.eligible_branches" class="form-control" placeholder="Eligible branches (comma-separated)" aria-label="Eligible Branches" />
                </div>
                <div class="col-md-4 mt-2">
                  <label class="form-label">Eligible Years</label>
                  <input v-model="newDrive.eligible_years" class="form-control" placeholder="Eligible years (comma-separated)" aria-label="Eligible Years" />
                </div>
                <div class="col-md-4 mt-2">
                  <label class="form-label">Job Type</label>
                  <input v-model="newDrive.job_type" class="form-control" placeholder="Job type" aria-label="Job Type" />
                </div>
                <div class="col-md-4 mt-2">
                  <label class="form-label">Employment Type</label>
                  <input v-model="newDrive.employment_type" class="form-control" placeholder="Employment type" aria-label="Employment Type" />
                </div>
              </div>
            </div>
          </transition>

          <div class="d-flex justify-content-between align-items-center mt-3">
            <div class="text-danger" v-if="errorMessage">{{ errorMessage }}</div>
            <div>
              <button class="btn btn-primary">Submit for Approval</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- List of this company's own drives -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h5 class="card-title">Created Placement Drives</h5>
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead>
              <tr>
                <th>Title</th>
                <th>Status</th>
                <th>Applicants</th>
                <th>Location</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="drive in myDrives" :key="drive.id">
                <td>{{ drive.title }}</td>
                <td><span class="badge" :class="drive.status === 'approved' ? 'bg-success' : 'bg-secondary'">{{ drive.status }}</span></td>
                <td>{{ drive.applicant_count }}</td>
                <td>{{ drive.location || 'N/A' }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary" @click="loadApplicants(drive.id)">View Applicants</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="myDrives.length === 0" class="text-muted mt-3 mb-0">No placement drives created yet.</p>
      </div>
    </div>

    <!-- Applicants for whichever drive was clicked above -->
    <div v-if="selectedDriveId">
      <h5>Applicants</h5>
      <table class="table">
        <thead><tr><th>Student</th><th>CGPA</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="app in applicants" :key="app.application_id">
            <td>{{ app.student_name }}</td>
            <td>{{ app.cgpa }}</td>
            <td>{{ app.status }}</td>
            <td>
              <select class="form-select form-select-sm" @change="showConfirmation(app.application_id, app.student_name, app.status, $event.target.value)">
                <option value="">Change status...</option>
                <option value="shortlisted">Shortlist</option>
                <option value="selected">Select</option>
                <option value="rejected">Reject</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="pendingStatusChange" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Status Change</h5>
            <button type="button" class="btn-close" @click="cancelStatusChange"></button>
          </div>
          <div class="modal-body">
            <p><strong>Student:</strong> {{ pendingStatusChange.studentName }}</p>
            <p><strong>Current Status:</strong> <span class="badge bg-secondary">{{ pendingStatusChange.currentStatus }}</span></p>
            <p><strong>New Status:</strong> <span class="badge bg-primary">{{ pendingStatusChange.newStatus }}</span></p>
            <p>Are you sure you want to proceed with this change?</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelStatusChange">Cancel</button>
            <button type="button" class="btn btn-primary" @click="confirmStatusChange">Confirm</button>
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
  name: 'CompanyDashboard',
  setup() {
    const auth = useAuthStore()
    return { auth }
  },
  data() {
    return {
      companyName: '',
      companyDetails: {},
      myDrives: [],
      applicants: [],
      selectedDriveId: null,
      newDrive: {
        title: '',
        package: '',
        salary_package: '',
        location: '',
        job_type: '',
        employment_type: '',
        placement_mode: '',
        min_cgpa: 0,
        description: '',
        skills_required: '',
        eligible_branches: '',
        eligible_years: '',
        application_deadline: '',
        drive_date: '',
      },
      showAdvanced: false,
      errorMessage: '',
      successMessage: '',
      pendingStatusChange: null,
    }
  },
  async mounted() {
    await this.loadCompanyProfile()
    await this.loadMyDrives()
  },
  methods: {
    async loadCompanyProfile() {
      try {
        const profile = await apiRequest('/companies/me', { token: this.auth.token })
        this.companyName = profile.company_name
        this.companyDetails = profile
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async loadMyDrives() {
      try {
        this.myDrives = await apiRequest('/drives/mine', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async handleCreateDrive() {
      this.errorMessage = ''
      this.successMessage = ''
      // Client-side validation: ensure application_deadline is strictly before drive_date
      if (this.newDrive.application_deadline && this.newDrive.drive_date) {
        const appDead = new Date(this.newDrive.application_deadline)
        const drv = new Date(this.newDrive.drive_date)
        if (isNaN(appDead.getTime()) || isNaN(drv.getTime())) {
          this.errorMessage = 'Invalid date format'
          return
        }
        if (appDead >= drv) {
          this.errorMessage = 'Drive date must be after the application deadline'
          return
        }
      }

      try {
        await apiRequest('/drives', {
          method: 'POST',
          token: this.auth.token,
          body: this.newDrive,
        })
        this.successMessage = 'Drive submitted for admin approval'
        this.newDrive = {
          title: '',
          package: '',
          salary_package: '',
          location: '',
          job_type: '',
          employment_type: '',
          placement_mode: '',
          min_cgpa: 0,
          description: '',
          skills_required: '',
          eligible_branches: '',
          eligible_years: '',
          application_deadline: '',
          drive_date: '',
        }
        await this.loadMyDrives()
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    statusClass(status) {
      const map = {
        approved: 'bg-success',
        pending: 'bg-warning text-dark',
        rejected: 'bg-danger',
      }
      return map[status] || 'bg-secondary'
    },
    async loadApplicants(driveId) {
      this.selectedDriveId = driveId
      try {
        this.applicants = await apiRequest(`/drives/${driveId}/applicants`, { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async updateStatus(applicationId, status) {
      if (!status) return
      try {
        await apiRequest(`/drives/applications/${applicationId}/status`, {
          method: 'PATCH',
          token: this.auth.token,
          body: { status },
        })
        await this.loadApplicants(this.selectedDriveId)
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    showConfirmation(applicationId, studentName, currentStatus, newStatus) {
      if (!newStatus) return
      this.pendingStatusChange = {
        applicationId,
        studentName,
        currentStatus,
        newStatus,
      }
    },
    async confirmStatusChange() {
      const { applicationId, newStatus } = this.pendingStatusChange
      await this.updateStatus(applicationId, newStatus)
      this.pendingStatusChange = null
    },
    cancelStatusChange() {
      this.pendingStatusChange = null
    },
  },
}
</script>
