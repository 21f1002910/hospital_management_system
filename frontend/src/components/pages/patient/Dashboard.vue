<script setup>
import { ref, onMounted } from 'vue'
import { patientAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const messageStore = useMessageStore()

const stats = ref({
  patient_name: '',
  upcoming_appointments: 0,
  past_appointments: 0,
  next_appointment: null
})

const loading = ref(false)

async function loadDashboard() {
  loading.value = true
  try {
    const response = await patientAPI.getDashboard()
    stats.value = response.data
  } catch (error) {
    console.error('Dashboard error:', error)
    messageStore.error('Failed to load dashboard data')
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

onMounted(() => {
  loadDashboard()
})
</script>

<template>
  <div class="container my-4">
    <h1 class="h3 fw-bold mb-1">Welcome, {{ stats.patient_name }}</h1>
    <p class="text-muted mb-4">Here's your health overview</p>

    <!-- Statistics Cards -->
    <div class="row g-3 mb-4">
      <div class="col-12 col-md-6 col-lg-4">
        <div class="card text-white h-100" style="background: linear-gradient(135deg,#3b82f6,#1d4ed8);">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <small class="opacity-75">Upcoming Appointments</small>
              <div class="h2 fw-bold mb-0">{{ stats.upcoming_appointments }}</div>
            </div>
            <div class="fs-1 opacity-25">📅</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card text-white h-100" style="background: linear-gradient(135deg,#22c55e,#15803d);">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <small class="opacity-75">Past Appointments</small>
              <div class="h2 fw-bold mb-0">{{ stats.past_appointments }}</div>
            </div>
            <div class="fs-1 opacity-25">✅</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card text-white h-100" style="background: linear-gradient(135deg,#a855f7,#6b21a8);">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <small class="opacity-75">Medical Records</small>
              <div class="h2 fw-bold mb-0">{{ stats.past_appointments }}</div>
            </div>
            <div class="fs-1 opacity-25">📋</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Next Appointment Card -->
    <div v-if="stats.next_appointment" class="card mb-4">
      <div class="card-body d-flex justify-content-between align-items-center">
        <div>
          <h5 class="fw-bold mb-1">Your Next Appointment</h5>
          <h3 class="text-primary fw-semibold mb-1">{{ stats.next_appointment.doctor_name }}</h3>
          <div class="text-muted mb-1">{{ stats.next_appointment.specialization }}</div>
          <div class="fw-medium">{{ formatDate(stats.next_appointment.date) }} at {{ stats.next_appointment.time }}</div>
        </div>

        <router-link
          :to="`/patient/appointments/${stats.next_appointment.id}`"
          class="btn btn-primary"
        >
          View Details →
        </router-link>
      </div>
    </div>

    <div v-else class="alert alert-warning mb-4 d-flex align-items-start">
      <div class="me-3 fs-3">📅</div>
      <div>
        <h6 class="fw-semibold mb-1">No Upcoming Appointments</h6>
        <p class="mb-2 text-warning">Schedule an appointment with our doctors</p>
        <router-link to="/patient/doctors" class="btn btn-warning btn-sm">Find a Doctor</router-link>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row g-3 mb-4">
      <div class="col-12 col-md-6 col-lg-3">
        <router-link to="/patient/doctors" class="card text-decoration-none text-dark h-100 shadow-sm">
          <div class="card-body text-center">
            <div class="fs-1 mb-2">🔍</div>
            <h6 class="fw-semibold mb-1">Find Doctors</h6>
            <div class="small text-muted">Search by specialization</div>
          </div>
        </router-link>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <router-link to="/patient/appointments" class="card text-decoration-none text-dark h-100 shadow-sm">
          <div class="card-body text-center">
            <div class="fs-1 mb-2">📅</div>
            <h6 class="fw-semibold mb-1">My Appointments</h6>
            <div class="small text-muted">View all appointments</div>
          </div>
        </router-link>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <router-link to="/patient/medical-history" class="card text-decoration-none text-dark h-100 shadow-sm">
          <div class="card-body text-center">
            <div class="fs-1 mb-2">📋</div>
            <h6 class="fw-semibold mb-1">Medical History</h6>
            <div class="small text-muted">View past records</div>
          </div>
        </router-link>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <router-link to="/patient/profile" class="card text-decoration-none text-dark h-100 shadow-sm">
          <div class="card-body text-center">
            <div class="fs-1 mb-2">👤</div>
            <h6 class="fw-semibold mb-1">My Profile</h6>
            <div class="small text-muted">Update information</div>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Page Loading (fallback) -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>