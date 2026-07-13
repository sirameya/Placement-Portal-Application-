<template>
  <div class="drive-card">
    <div class="drive-main">
      <div>
        <h6>{{ drive.title }}</h6>
        <p class="company-line">{{ drive.company }}</p>
        <p class="meta-line">{{ drive.package || 'Package not specified' }} · Min CGPA: {{ drive.min_cgpa }}</p>
      </div>
      <button 
        v-if="showApplyButton" 
        class="apply-btn" 
        :disabled="isApplied"
        :class="{ applied: isApplied }"
        @click="$emit('apply', drive.id)">
        {{ isApplied ? 'Applied' : 'Apply' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DriveCard',
  props: {
    drive: { type: Object, required: true },
    showApplyButton: { type: Boolean, default: true },
    isApplied: { type: Boolean, default: false },
  },
  emits: ['apply'],
}
</script>

<style scoped>
.drive-card {
  border: 1px solid #e5edff;
  border-radius: 16px;
  padding: 1rem;
  background: linear-gradient(135deg, #ffffff, #f8fbff);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}
.drive-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.drive-main h6 {
  margin: 0 0 0.25rem;
  font-weight: 700;
}
.company-line {
  margin: 0;
  color: #2563eb;
  font-weight: 600;
}
.meta-line {
  margin: 0.3rem 0 0;
  color: #64748b;
  font-size: 0.9rem;
}
.apply-btn {
  border: none;
  border-radius: 999px;
  padding: 0.55rem 0.95rem;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
.apply-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-2px);
}
.apply-btn:disabled {
  background: #cbd5e1;
  color: #475569;
  cursor: not-allowed;
  opacity: 0.7;
}
.apply-btn.applied {
  background: #10b981;
}
@media (max-width: 700px) {
  .drive-main {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
