<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-lg-3 mb-4">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Navigation</h5>
            <div class="nav nav-pills flex-column">
              <button class="nav-link text-start" :class="{ active: activeTab === 'profile' }" type="button" @click="activeTab = 'profile'">Profile</button>
              <button class="nav-link text-start" :class="{ active: activeTab === 'create' }" type="button" @click="activeTab = 'create'">Create Drive</button>
              <button class="nav-link text-start" :class="{ active: activeTab === 'drives' }" type="button" @click="activeTab = 'drives'">My Drives</button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-9">
        <div v-if="activeTab === 'profile'" class="card mb-4 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 class="card-title mb-0">Company Profile</h5>
                <small class="text-muted">View and edit your company details.</small>
              </div>
              <button type="button" class="btn btn-outline-primary btn-sm" @click="toggleProfileEdit">
                {{ isEditingProfile ? 'Cancel Edit' : 'Edit Profile' }}
              </button>
            </div>

            <div v-if="profileSaveSuccess" class="alert alert-success">{{ profileSaveSuccess }}</div>
            <div v-if="profileSaveError" class="alert alert-danger">{{ profileSaveError }}</div>

            <form @submit.prevent="saveCompanyProfile" class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Company Name</label>
                <input v-model="companyForm.company_name" :readonly="!isEditingProfile" class="form-control" required aria-label="Company Name" />
              </div>
              <div class="col-md-6">
                <label class="form-label">HR Contact</label>
                <input v-model="companyForm.hr_contact" :readonly="!isEditingProfile" class="form-control" aria-label="HR Contact" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Website</label>
                <input v-model="companyForm.website" :readonly="!isEditingProfile" class="form-control" aria-label="Website" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Industry</label>
                <input v-model="companyForm.industry" :readonly="!isEditingProfile" class="form-control" aria-label="Industry" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Address</label>
                <input v-model="companyForm.address" :readonly="!isEditingProfile" class="form-control" aria-label="Address" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Contact Email</label>
                <input v-model="companyForm.contact_email" type="email" :readonly="!isEditingProfile" class="form-control" aria-label="Contact Email" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Phone Number</label>
                <input v-model="companyForm.phone_number" :readonly="!isEditingProfile" class="form-control" aria-label="Phone Number" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Employee Count</label>
                <input v-model.number="companyForm.employee_count" type="number" min="0" :readonly="!isEditingProfile" class="form-control" aria-label="Employee Count" />
              </div>
              <div class="col-12">
                <label class="form-label">Description</label>
                <textarea v-model="companyForm.description" :readonly="!isEditingProfile" class="form-control" rows="3" aria-label="Description"></textarea>
              </div>
              <div class="col-12 text-end" v-if="isEditingProfile">
                <button type="submit" class="btn btn-primary">Save Profile</button>
              </div>
            </form>
          </div>
        </div>

        <div v-if="activeTab === 'create'" class="card mb-4">
          <div class="card-body">
            <h5 class="card-title">Create New Drive</h5>
            <form @submit.prevent="handleCreateDrive" class="card p-3 shadow-sm">
          <div class="d-flex align-items-center justify-content-between mb-2">
            <div>
              <h5 class="mb-0">{{ editDriveId ? 'Edit Drive' : 'Create New Drive' }}</h5>
              <small class="text-muted">Keep it short and attractive — students notice clear titles.</small>
            </div>
            <div>
              <button type="button" class="btn btn-outline-secondary btn-sm me-2" @click="showAdvanced = !showAdvanced">
                {{ showAdvanced ? 'Hide Advanced' : 'Advanced options' }}
              </button>
              <button v-if="editDriveId" type="button" class="btn btn-outline-danger btn-sm" @click="cancelEditDrive">
                Cancel Edit
              </button>
            </div>
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
              <button class="btn btn-primary">{{ editDriveId ? 'Save Changes' : 'Submit for Approval' }}</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div v-if="activeTab === 'drives'">
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
                    <button class="btn btn-sm btn-outline-secondary me-2" @click="editDrive(drive)">Edit</button>
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
      companyForm: {
        company_name: '',
        hr_contact: '',
        website: '',
        industry: '',
        address: '',
        contact_email: '',
        phone_number: '',
        description: '',
        employee_count: null,
      },
      profileSaveSuccess: '',
      profileSaveError: '',
      myDrives: [],
      applicants: [],
      selectedDriveId: null,
      editDriveId: null,
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
      activeTab: 'profile',
      showAdvanced: false,
      isEditingProfile: false,
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
        this.companyForm = {
          company_name: profile.company_name || '',
          hr_contact: profile.hr_contact || '',
          website: profile.website || '',
          industry: profile.industry || '',
          address: profile.address || '',
          contact_email: profile.contact_email || '',
          phone_number: profile.phone_number || '',
          description: profile.description || '',
          employee_count: profile.employee_count || null,
        }
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    async saveCompanyProfile() {
      this.profileSaveSuccess = ''
      this.profileSaveError = ''
      try {
        const result = await apiRequest('/companies/me', {
          method: 'PATCH',
          token: this.auth.token,
          body: this.companyForm,
        })
        this.profileSaveSuccess = result.message || 'Profile updated successfully.'
        this.companyDetails = result.company
        this.isEditingProfile = false
      } catch (err) {
        this.profileSaveError = err.message
      }
    },
    toggleProfileEdit() {
      if (this.isEditingProfile) {
        this.isEditingProfile = false
        this.companyForm = {
          company_name: this.companyDetails.company_name || '',
          hr_contact: this.companyDetails.hr_contact || '',
          website: this.companyDetails.website || '',
          industry: this.companyDetails.industry || '',
          address: this.companyDetails.address || '',
          contact_email: this.companyDetails.contact_email || '',
          phone_number: this.companyDetails.phone_number || '',
          description: this.companyDetails.description || '',
          employee_count: this.companyDetails.employee_count || null,
        }
      } else {
        this.isEditingProfile = true
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

      const endpoint = this.editDriveId ? `/drives/${this.editDriveId}` : '/drives'
      const method = this.editDriveId ? 'PATCH' : 'POST'

      try {
        await apiRequest(endpoint, {
          method,
          token: this.auth.token,
          body: this.newDrive,
        })
        this.successMessage = this.editDriveId ? 'Drive updated successfully' : 'Drive submitted for admin approval'
        this.cancelEditDrive()
        await this.loadMyDrives()
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    editDrive(drive) {
      this.activeTab = 'create'
      this.editDriveId = drive.id
      this.showAdvanced = true
      this.newDrive = {
        title: drive.title || '',
        package: drive.package || '',
        salary_package: drive.salary_package || '',
        location: drive.location || '',
        job_type: drive.job_type || '',
        employment_type: drive.employment_type || '',
        placement_mode: drive.placement_mode || '',
        min_cgpa: drive.min_cgpa || 0,
        description: drive.description || '',
        skills_required: drive.skills_required || '',
        eligible_branches: drive.eligible_branches || '',
        eligible_years: drive.eligible_years || '',
        application_deadline: drive.application_deadline ? this.toDateTimeLocal(drive.application_deadline) : '',
        drive_date: drive.drive_date ? this.toDateTimeLocal(drive.drive_date) : '',
      }
    },
    cancelEditDrive() {
      this.editDriveId = null
      this.successMessage = ''
      this.errorMessage = ''
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
    },
    toDateTimeLocal(value) {
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return ''
      return date.toISOString().slice(0, 16)
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
