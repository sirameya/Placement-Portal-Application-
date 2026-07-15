<template>
  <div class="drive-card">
    <div class="drive-main">
      <div>
        <h6>{{ drive.title }}</h6>
        <p class="company-line">{{ drive.company }}</p>
        <p class="meta-line">{{ drive.package || 'Package not specified' }} · {{ drive.location || 'Location TBD' }} · Min CGPA: {{ drive.min_cgpa }}</p>
        <p v-if="drive.skills_required" class="meta-line">Skills: {{ drive.skills_required }}</p>
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
  box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.drive-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
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
  color: #0f172a;
}
.company-line {
  margin: 0;
  color: #2563eb;
  font-weight: 600;
}
.meta-line {
  margin: 0.3rem 0 0;
  color: #475569;
  font-size: 0.92rem;
}
.apply-btn {
  border: none;
  border-radius: 999px;
  padding: 0.55rem 1rem;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.apply-btn:hover:not(:disabled) {
  opacity: 0.94;
  transform: translateY(-1px);
}
.apply-btn:disabled {
  background: #cbd5e1;
  color: #475569;
  cursor: not-allowed;
  opacity: 0.8;
}
.apply-btn.applied {
  background: #10b981;
}
@media (max-width: 700px) {
  .drive-main {
    flex-direction: column;
    align-items: stretch;
  }
  .apply-btn {
    width: 100%;
  }
}
</style>
