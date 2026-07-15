<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h3 class="mb-1">Admin Charts</h3>
        <p class="text-muted mb-0">Visualize platform stats and drive approvals.</p>
      </div>
      <router-link class="btn btn-outline-secondary" to="/admin">Back to Dashboard</router-link>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

    <div class="row g-4">
      <div class="col-lg-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title">Platform Activity</h5>
            <canvas ref="statsCanvas" height="240"></canvas>
          </div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title">Drive Approval Status</h5>
            <canvas ref="approvalCanvas" height="240"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiRequest } from '../api'
import { useAuthStore } from '../stores/auth'
import Chart from 'chart.js/auto'

export default {
  name: 'AdminCharts',
  setup() {
    const auth = useAuthStore()
    return { auth }
  },
  data() {
    return {
      stats: {
        total_students: 0,
        total_companies: 0,
        total_drives: 0,
        total_selected: 0,
      },
      drives: [],
      pendingDrives: [],
      errorMessage: '',
      charts: {
        stats: null,
        approval: null,
      },
    }
  },
  async mounted() {
    await Promise.all([
      this.loadStats(),
      this.loadDrives(),
      this.loadPendingDrives(),
    ])
    this.createCharts()
  },
  methods: {
    async loadStats() {
      try {
        this.stats = await apiRequest('/drives/stats', { token: this.auth.token })
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
    async loadPendingDrives() {
      try {
        this.pendingDrives = await apiRequest('/drives/pending', { token: this.auth.token })
      } catch (err) {
        this.errorMessage = err.message
      }
    },
    createCharts() {
      const statsCtx = this.$refs.statsCanvas?.getContext('2d')
      const approvalCtx = this.$refs.approvalCanvas?.getContext('2d')

      if (!statsCtx || !approvalCtx) {
        return
      }

      const statValues = [
        this.stats.total_students,
        this.stats.total_companies,
        this.stats.total_drives,
        this.stats.total_selected,
      ]

      if (this.charts.stats) {
        this.charts.stats.destroy()
      }
      this.charts.stats = new Chart(statsCtx, {
        type: 'bar',
        data: {
          labels: ['Students', 'Companies', 'Drives', 'Selected'],
          datasets: [
            {
              label: 'Count',
              data: statValues,
              backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#0dcaf0'],
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
          },
        },
      })

      const approvedCount = this.drives.filter((d) => d.status === 'approved').length
      const rejectedCount = this.drives.filter((d) => d.status === 'rejected').length
      const pendingCount = this.pendingDrives.length

      if (this.charts.approval) {
        this.charts.approval.destroy()
      }
      this.charts.approval = new Chart(approvalCtx, {
        type: 'doughnut',
        data: {
          labels: ['Approved', 'Rejected', 'Pending'],
          datasets: [
            {
              data: [approvedCount, rejectedCount, pendingCount],
              backgroundColor: ['#198754', '#dc3545', '#ffc107'],
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom' },
          },
        },
      })
    },
  },
}
</script>
