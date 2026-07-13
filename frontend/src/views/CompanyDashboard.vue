<template>
  <div class="container mt-4">
    <h3>Company Dashboard</h3>
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

    <!-- Create a new drive -->
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Create New Drive</h5>
        <form @submit.prevent="handleCreateDrive" class="row g-2">
          <div class="col-md-4"><input v-model="newDrive.title" class="form-control" placeholder="Title" required /></div>
          <div class="col-md-3"><input v-model="newDrive.package" class="form-control" placeholder="Package (e.g. 6 LPA)" /></div>
          <div class="col-md-2"><input v-model.number="newDrive.min_cgpa" type="number" step="0.1" class="form-control" placeholder="Min CGPA" /></div>
          <div class="col-md-3"><textarea v-model="newDrive.description" class="form-control" placeholder="Description"></textarea></div>
          <div class="col-12"><button class="btn btn-primary btn-sm">Submit for Approval</button></div>
        </form>
      </div>
    </div>

    <!-- List of this company's own drives -->
    <h5>My Drives</h5>
    <table class="table">
      <thead><tr><th>Title</th><th>Status</th><th>Applicants</th><th></th></tr></thead>
      <tbody>
        <tr v-for="drive in myDrives" :key="drive.id">
          <td>{{ drive.title }}</td>
          <td><span class="badge" :class="drive.status === 'approved' ? 'bg-success' : 'bg-secondary'">{{ drive.status }}</span></td>
          <td>{{ drive.applicant_count }}</td>
          <td>
            <button class="btn btn-sm btn-outline-primary" @click="loadApplicants(drive.id)">View Applicants</button>
          </td>
        </tr>
      </tbody>
    </table>

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
      myDrives: [],
      applicants: [],
      selectedDriveId: null,
      newDrive: { title: '', package: '', min_cgpa: 0, description: '' },
      errorMessage: '',
      successMessage: '',
      pendingStatusChange: null,
    }
  },
  async mounted() {
    await this.loadMyDrives()
  },
  methods: {
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
      try {
        await apiRequest('/drives', {
          method: 'POST',
          token: this.auth.token,
          body: this.newDrive,
        })
        this.successMessage = 'Drive submitted for admin approval'
        this.newDrive = { title: '', package: '', min_cgpa: 0, description: '' }
        await this.loadMyDrives()
      } catch (err) {
        this.errorMessage = err.message
      }
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
