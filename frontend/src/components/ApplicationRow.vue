<template>
  <tr>
    <td>{{ application.drive_title }}</td>
    <td>{{ application.company }}</td>
    <td>{{ application.applied_on }}</td>
    <td>
      <span class="badge" :class="statusBadgeClass">{{ application.status }}</span>
    </td>
  </tr>
</template>

<script>
export default {
  name: 'ApplicationRow',
  props: {
    application: { type: Object, required: true },
  },
  computed: {
    // A "computed" property recalculates automatically whenever
    // application.status changes — no need to manually update it.
    statusBadgeClass() {
      const colors = {
        applied: 'bg-secondary',
        shortlisted: 'bg-warning text-dark',
        selected: 'bg-success',
        rejected: 'bg-danger',
      }
      return colors[this.application.status] || 'bg-secondary'
    },
  },
}
</script>
