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
      <div class="col-lg-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title">Platform Activity</h5>
            <canvas ref="statsCanvas" height="240"></canvas>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title">Drive Approval Status</h5>
            <canvas ref="approvalCanvas" height="240"></canvas>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title">Application Status Breakdown</h5>
            <canvas ref="appStatusCanvas" height="240"></canvas>
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
        application_status_counts: {
          applied: 0,
          shortlisted: 0,
          selected: 0,
          rejected: 0,
        },
      },
      drives: [],
      pendingDrives: [],
      errorMessage: '',
      charts: {
        stats: null,
        approval: null,
        application: null,
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
  beforeUnmount() {
    this.destroyCharts()
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
    destroyCharts() {
      Object.keys(this.charts).forEach((key) => {
        if (this.charts[key]) {
          this.charts[key].destroy()
          this.charts[key] = null
        }
      })
    },
    createCharts() {
      const statsCtx = this.$refs.statsCanvas?.getContext('2d')
      const approvalCtx = this.$refs.approvalCanvas?.getContext('2d')
      const appStatusCtx = this.$refs.appStatusCanvas?.getContext('2d')

      if (!statsCtx || !approvalCtx || !appStatusCtx) {
        return
      }

      const statValues = [
        Number(this.stats.total_students),
        Number(this.stats.total_companies),
        Number(this.stats.total_drives),
        Number(this.stats.total_selected),
      ]

      const approvedCount = this.drives.filter((d) => d.status === 'approved').length
      const rejectedCount = this.drives.filter((d) => d.status === 'rejected').length
      const pendingCount = this.pendingDrives.length

      const applicationData = [
        Number(this.stats.application_status_counts.applied),
        Number(this.stats.application_status_counts.shortlisted),
        Number(this.stats.application_status_counts.selected),
        Number(this.stats.application_status_counts.rejected),
      ]

      if (this.charts.stats) {
        this.charts.stats.data.datasets[0].data = statValues
        this.charts.stats.update()
      } else {
        this.charts.stats = new Chart(statsCtx, {
          type: 'bar',
          data: {
            labels: ['Students', 'Companies', 'Drives', 'Selected'],
            datasets: [
              {
                label: 'Count',
                data: statValues,
                backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#0dcaf0'],
                borderRadius: 12,
                maxBarThickness: 42,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: {
                grid: { display: false },
              },
              y: {
                beginAtZero: true,
                ticks: { precision: 0 },
              },
            },
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: (context) => `${context.dataset.label}: ${context.formattedValue}`,
                },
              },
            },
          },
        })
      }

      if (this.charts.approval) {
        this.charts.approval.data.datasets[0].data = [approvedCount, rejectedCount, pendingCount]
        this.charts.approval.update()
      } else {
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
              tooltip: {
                callbacks: {
                  label: (context) => `${context.label}: ${context.formattedValue}`,
                },
              },
            },
          },
        })
      }

      if (this.charts.application) {
        this.charts.application.data.datasets[0].data = applicationData
        this.charts.application.update()
      } else {
        this.charts.application = new Chart(appStatusCtx, {
          type: 'pie',
          data: {
            labels: ['Applied', 'Shortlisted', 'Selected', 'Rejected'],
            datasets: [
              {
                data: applicationData,
                backgroundColor: ['#0d6efd', '#6610f2', '#198754', '#dc3545'],
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom' },
              tooltip: {
                callbacks: {
                  label: (context) => `${context.label}: ${context.formattedValue}`,
                },
              },
            },
          },
        })
      }
    },
  },
}
</script>
