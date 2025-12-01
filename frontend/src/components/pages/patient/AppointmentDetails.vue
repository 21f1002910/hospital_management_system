<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { patientAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()
const headerGradientStyle = 'background: linear-gradient(135deg,#3b82f6,#1e40af);';

const appointment = ref(null)
const loading = ref(false)

async function loadAppointment() {
  loading.value = true
  try {
    const response = await patientAPI.getAppointment(route.params.id)
    appointment.value = response.data
  } catch (error) {
    console.error('Load appointment error:', error)
    messageStore.error('Failed to load appointment details')
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { 
    weekday: 'long',
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

function openRescheduleModal() {
  // Implement reschedule modal or redirect to appointments page
  router.push('/patient/appointments')
}

function confirmCancel() {
  if (confirm('Are you sure you want to cancel this appointment?')) {
    cancelAppointment()
  }
}

async function cancelAppointment() {
  try {
    await patientAPI.cancelAppointment(appointment.value.id)
    messageStore.success('Appointment cancelled successfully')
    router.push('/patient/appointments')
  } catch (error) {
    console.error('Cancel error:', error)
    messageStore.error('Failed to cancel appointment')
  }
}

onMounted(() => {
  loadAppointment()
})
</script>

<style>
@media print {
  button, nav {
    display: none !important;
  }
}
</style>


<template>
  <div class="container my-4">
    <button @click="$router.back()" class="btn btn-link mb-4">
      ← Back to Appointments
    </button>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>

    <!-- Appointment -->
    <div v-else-if="appointment">
      <!-- Header -->
      <div class="card text-white mb-4" :style="headerGradientStyle">
        <div class="card-body d-flex justify-content-between align-items-start">
          <div>
            <span
              class="badge mb-3"
              :class="appointment.status === 'Booked' ? 'bg-light text-primary' : appointment.status === 'Completed' ? 'bg-success text-white' : 'bg-danger text-white'"
            >
              {{ appointment.status }}
            </span>

            <h1 class="h3 fw-bold mb-1">Appointment Details</h1>
            <p class="mb-0 lead text-white-50">
              {{ formatDate(appointment.date) }} at {{ formatTime(appointment.time) }}
            </p>
          </div>

          <div class="display-3 opacity-25">📅</div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Main -->
        <div class="col-12 col-lg-8">
          <!-- Doctor Information -->
          <div class="card mb-3">
            <div class="card-body">
              <h5 class="fw-bold mb-3">
                <span class="me-2">👨‍⚕️</span>Doctor Information
              </h5>

              <div class="row">
                <div class="col-12 col-md-6 mb-2">
                  <div class="small text-muted">Doctor Name</div>
                  <div class="fw-medium">{{ appointment.doctor.name }}</div>
                </div>

                <div class="col-12 col-md-6 mb-2">
                  <div class="small text-muted">Specialization</div>
                  <div class="text-primary fw-medium">{{ appointment.doctor.specialization }}</div>
                </div>

                <div v-if="appointment.doctor.contact" class="col-12 col-md-6">
                  <div class="small text-muted">Contact</div>
                  <div class="fw-medium">{{ appointment.doctor.contact }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Appointment Information -->
          <div class="card mb-3">
            <div class="card-body">
              <h5 class="fw-bold mb-3"><span class="me-2">📋</span>Appointment Information</h5>

              <div class="row">
                <div class="col-12 col-md-6 mb-2">
                  <div class="small text-muted">Date & Time</div>
                  <div class="fw-medium">{{ formatDate(appointment.date) }} at {{ formatTime(appointment.time) }}</div>
                </div>

                <div class="col-12 col-md-6 mb-2">
                  <div class="small text-muted">Status</div>
                  <div>
                    <span
                      class="badge"
                      :class="appointment.status === 'Booked' ? 'bg-primary' : appointment.status === 'Completed' ? 'bg-success' : 'bg-danger'"
                    >
                      {{ appointment.status }}
                    </span>
                  </div>
                </div>
              </div>

              <div v-if="appointment.reason" class="mt-3">
                <div class="small text-muted">Reason for Visit</div>
                <div class="fw-medium">{{ appointment.reason }}</div>
              </div>

              <div v-if="appointment.notes" class="mt-3">
                <div class="small text-muted">Notes</div>
                <div class="fw-medium">{{ appointment.notes }}</div>
              </div>
            </div>
          </div>

          <!-- Treatment & Prescription -->
          <div v-if="appointment.treatment" class="card mb-3">
            <div class="card-body">
              <h5 class="fw-bold mb-3"><span class="me-2">💊</span>Treatment & Prescription</h5>

              <!-- Diagnosis -->
              <div class="card mb-3 border-0" style="background-color:#eff6ff;">
                <div class="card-body p-3">
                  <div class="d-flex">
                    <div class="me-3 fs-3">🔬</div>
                    <div>
                      <div class="small text-primary fw-semibold">DIAGNOSIS</div>
                      <div class="fw-medium">{{ appointment.treatment.diagnosis }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Prescription -->
              <div v-if="appointment.treatment.prescription" class="card mb-3 border-0" style="background-color:#ecfdf5;">
                <div class="card-body p-3">
                  <div class="d-flex">
                    <div class="me-3 fs-3">💊</div>
                    <div>
                      <div class="small text-success fw-semibold">PRESCRIPTION</div>
                      <pre class="mb-0" style="white-space:pre-wrap;">{{ appointment.treatment.prescription }}</pre>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Notes -->
              <div v-if="appointment.treatment.notes" class="card mb-3 border-0" style="background-color:#fff7ed;">
                <div class="card-body p-3">
                  <div class="d-flex">
                    <div class="me-3 fs-3">📝</div>
                    <div>
                      <div class="small text-warning fw-semibold">DOCTOR'S NOTES</div>
                      <div>{{ appointment.treatment.notes }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Next Visit -->
              <div v-if="appointment.treatment.next_visit_date" class="card border-0" style="background-color:#f5f3ff;">
                <div class="card-body p-3 d-flex align-items-center">
                  <div class="me-3 fs-3">📅</div>
                  <div>
                    <div class="small text-purple fw-semibold">NEXT VISIT</div>
                    <div class="fw-medium">{{ formatDate(appointment.treatment.next_visit_date) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="appointment.status === 'Completed'" class="card mb-3">
            <div class="card-body text-center text-muted">
              No treatment record available for this appointment
            </div>
          </div>
        </div>

        <!-- Sidebar actions -->
        <div class="col-12 col-lg-4">
          <div class="card position-sticky" style="top:1rem;">
            <div class="card-body">
              <h6 class="fw-bold mb-3">Quick Actions</h6>

              <div class="d-grid gap-2">
                <button
                  v-if="appointment.status === 'Booked'"
                  @click="openRescheduleModal"
                  class="btn btn-warning"
                >
                  Reschedule
                </button>

                <button
                  v-if="appointment.status === 'Booked'"
                  @click="confirmCancel"
                  class="btn btn-danger"
                >
                  Cancel Appointment
                </button>

                <router-link to="/patient/appointments" class="btn btn-light text-start">
                  View All Appointments
                </router-link>

                <button
                  v-if="appointment.treatment"
                  @click="window.print()"
                  class="btn btn-primary"
                >
                  🖨️ Print Record
                </button>
              </div>

              <div class="mt-4 pt-3 border-top">
                <p class="small text-muted mb-0">
                  Need help? Contact the clinic for any questions about your appointment.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Note: Modals (reschedule / cancel) should be implemented as separate components or v-if blocks similar to your other views -->
  </div>
</template>