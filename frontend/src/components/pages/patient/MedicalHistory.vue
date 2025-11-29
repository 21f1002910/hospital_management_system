<script setup>
import { ref, computed, onMounted } from 'vue'
import { patientAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'


const messageStore = useMessageStore()

const history = ref([])
const loading = ref(false)

const uniqueDoctors = computed(() => {
  const doctors = new Set(history.value.map(r => r.doctor_name))
  return doctors.size
})

const uniqueSpecializations = computed(() => {
  const specs = new Set(history.value.map(r => r.specialization))
  return specs.size
})

async function loadHistory() {
  loading.value = true
  try {
    const response = await patientAPI.getMedicalHistory()
    history.value = response.data.history
  } catch (error) {
    console.error('Load medical history error:', error)
    messageStore.error('Failed to load medical history')
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { 
    weekday: 'short',
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

function formatTime(time) {
  const [hours, minutes] = time.split(':')
  const hour = parseInt(hours)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const displayHour = hour % 12 || 12
  return `${displayHour}:${minutes} ${ampm}`
}

onMounted(() => {
  loadHistory()
})
</script>


<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 fw-bold text-dark mb-0">Medical History</h1>
      <button
        v-if="history.length > 0"
        @click="window.print()"
        class="btn btn-primary px-4 py-2 fw-medium"
      >
        🖨️ Print History
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="history.length === 0"
      class="bg-white rounded shadow p-5 text-center text-muted"
    >
      <div class="display-3 mb-3">📋</div>
      <p class="h5 fw-semibold mb-2">No Medical History</p>
      <p class="small mb-4">
        Your completed appointments and treatments will appear here
      </p>
      <router-link
        to="/patient/doctors"
        class="btn btn-primary px-4 py-2 fw-medium"
      >
        Book an Appointment
      </router-link>
    </div>

    <!-- Content -->
    <div v-else class="d-flex flex-column gap-4">
      <!-- Summary Card -->
      <div class="bg-gradient-to-br rounded shadow-lg p-4 text-white">
        <h2 class="h4 fw-bold mb-1">Your Health Records</h2>
        <p class="mb-3 opacity-75">Complete history of all your medical consultations</p>
        <div class="row g-3">
          <div class="col-12 col-md-4">
            <p class="h3 fw-bold mb-0">{{ history.length }}</p>
            <p class="small opacity-75 mb-0">Total Visits</p>
          </div>
          <div class="col-12 col-md-4">
            <p class="h3 fw-bold mb-0">{{ uniqueDoctors }}</p>
            <p class="small opacity-75 mb-0">Doctors Consulted</p>
          </div>
          <div class="col-12 col-md-4">
            <p class="h3 fw-bold mb-0">{{ uniqueSpecializations }}</p>
            <p class="small opacity-75 mb-0">Specializations</p>
          </div>
        </div>
      </div>

      <!-- Timeline -->
      <div class="d-flex flex-column gap-4">
        <div
          v-for="(record, index) in history"
          :key="record.id"
          class="bg-white rounded shadow-sm hover-shadow transition"
        >
          <!-- Header -->
          <div class="p-4 border-bottom bg-light">
            <div class="d-flex justify-content-between">
              <div>
                <div class="d-flex align-items-center mb-2">
                  <div
                    class="d-flex align-items-center justify-content-center rounded-circle bg-primary bg-opacity-10 text-primary fw-bold me-3"
                    style="width: 40px; height: 40px;"
                  >
                    {{ index + 1 }}
                  </div>
                  <h3 class="h5 fw-semibold text-dark mb-0">
                    Dr. {{ record.doctor_name }}
                  </h3>
                </div>
                <p class="text-primary fw-medium mb-1">
                  {{ record.specialization }}
                </p>
                <div class="d-flex flex-wrap align-items-center gap-3 small text-muted">
                  <span class="d-flex align-items-center">
                    <span class="me-1">📅</span>
                    {{ formatDate(record.date) }}
                  </span>
                  <span class="d-flex align-items-center">
                    <span class="me-1">🕐</span>
                    {{ formatTime(record.time) }}
                  </span>
                </div>
                <p
                  v-if="record.reason"
                  class="small text-dark mt-2 d-inline-block px-3 py-1 bg-primary bg-opacity-10 rounded-pill"
                >
                  {{ record.reason }}
                </p>
              </div>
              <div class="text-end">
                <span class="small text-muted">Visit #{{ history.length - index }}</span>
              </div>
            </div>
          </div>

          <!-- Treatment Details -->
          <div class="p-4">
            <div v-if="record.treatment" class="d-flex flex-column gap-3">
              <!-- Diagnosis -->
              <div class="bg-primary bg-opacity-10 rounded p-3 border-start border-4 border-primary">
                <div class="d-flex">
                  <span class="fs-3 me-3">🔬</span>
                  <div class="flex-grow-1">
                    <p class="small fw-semibold text-primary text-uppercase mb-1">
                      Diagnosis
                    </p>
                    <p class="mb-0 text-dark">
                      {{ record.treatment.diagnosis }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Prescription -->
              <div
                v-if="record.treatment.prescription"
                class="bg-success bg-opacity-10 rounded p-3 border-start border-4 border-success"
              >
                <div class="d-flex">
                  <span class="fs-3 me-3">💊</span>
                  <div class="flex-grow-1">
                    <p class="small fw-semibold text-success text-uppercase mb-1">
                      Prescription
                    </p>
                    <p class="mb-0 text-dark white-space-pre-line">
                      {{ record.treatment.prescription }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Notes -->
              <div
                v-if="record.treatment.notes"
                class="bg-warning bg-opacity-10 rounded p-3 border-start border-4 border-warning"
              >
                <div class="d-flex">
                  <span class="fs-3 me-3">📝</span>
                  <div class="flex-grow-1">
                    <p class="small fw-semibold text-warning text-uppercase mb-1">
                      Doctor's Notes
                    </p>
                    <p class="mb-0 text-dark">
                      {{ record.treatment.notes }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Next Visit -->
              <div
                v-if="record.treatment.next_visit_date"
                class="bg-light rounded p-3 border-start border-4 border-secondary"
              >
                <div class="d-flex align-items-center">
                  <span class="fs-3 me-3">📅</span>
                  <div class="flex-grow-1">
                    <p class="small fw-semibold text-secondary text-uppercase mb-1">
                      Follow-up Visit
                    </p>
                    <p class="mb-0 fw-medium text-dark">
                      {{ formatDate(record.treatment.next_visit_date) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-4 text-muted">
              <p class="small mb-0">No treatment details recorded for this visit</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Export Options -->
      <div class="bg-white rounded shadow p-4">
        <h3 class="h6 fw-semibold text-dark mb-3">Export Options</h3>
        <div class="d-flex flex-column flex-md-row gap-3">
          <button
            @click="window.print()"
            class="btn btn-primary flex-fill px-4 py-2 fw-medium"
          >
            🖨️ Print Records
          </button>
          <button
            class="btn btn-light flex-fill px-4 py-2 fw-medium"
          >
            📧 Email to Doctor
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.bg-gradient-to-br {
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
}

/* Optional: preserve whitespace for prescription text */
.white-space-pre-line {
  white-space: pre-line;
}

.hover-shadow:hover {
  box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .15);
}

@media print {
  button,
  nav,
  .no-print {
    display: none !important;
  }

  .bg-gradient-to-br {
    background: #8b5cf6 !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
</style>
