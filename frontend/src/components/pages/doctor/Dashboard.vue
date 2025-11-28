<script setup>
import { ref, onMounted } from 'vue'
import { doctorAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const messageStore = useMessageStore()

const stats = ref({
  doctor_name: '',
  todays_appointments: 0,
  week_appointments: 0,
  completed_appointments: 0,
  total_patients: 0
})

const todaysAppointments = ref([])
const loading = ref(false)
const loadingToday = ref(false)

async function loadDashboard() {
  loading.value = true
  try {
    const response = await doctorAPI.getDashboard()
    stats.value = response.data
  } catch (error) {
    console.error('Dashboard error:', error)
    messageStore.error('Failed to load dashboard data')
  } finally {
    loading.value = false
  }
}

async function loadTodaysAppointments() {
  loadingToday.value = true
  try {
    const response = await doctorAPI.getAppointments({ view: 'today', per_page: 5 })
    todaysAppointments.value = response.data.appointments
  } catch (error) {
    console.error('Todays appointments error:', error)
  } finally {
    loadingToday.value = false
  }
}

onMounted(() => {
  loadDashboard()
  loadTodaysAppointments()
})
</script>

<template>
  <div class="container my-4">

    <!-- Header -->
    <h1 class="h3 fw-bold mb-1">Welcome, {{ stats.doctor_name }}</h1>
    <p class="text-muted mb-4">Here's your schedule overview</p>

    <!-- Statistics Cards -->
    <div class="row g-3 mb-4">

      <div class="col-12 col-md-6 col-lg-3">
        <div class="card text-white h-100" style="background: linear-gradient(135deg,#3b82f6,#1d4ed8);">
          <div class="card-body d-flex justify-content-between">
            <div>
              <h6 class="opacity-75 mb-1">Today's Appointments</h6>
              <h2 class="fw-bold">{{ stats.todays_appointments }}</h2>
            </div>
            <div class="fs-1 opacity-25">📅</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <div class="card text-white h-100" style="background: linear-gradient(135deg,#22c55e,#15803d);">
          <div class="card-body d-flex justify-content-between">
            <div>
              <h6 class="opacity-75 mb-1">This Week</h6>
              <h2 class="fw-bold">{{ stats.week_appointments }}</h2>
            </div>
            <div class="fs-1 opacity-25">📊</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <div class="card text-white h-100" style="background: linear-gradient(135deg,#a855f7,#6b21a8);">
          <div class="card-body d-flex justify-content-between">
            <div>
              <h6 class="opacity-75 mb-1">Completed</h6>
              <h2 class="fw-bold">{{ stats.completed_appointments }}</h2>
            </div>
            <div class="fs-1 opacity-25">✅</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <div class="card text-white h-100" style="background: linear-gradient(135deg,#fb923c,#ea580c);">
          <div class="card-body d-flex justify-content-between">
            <div>
              <h6 class="opacity-75 mb-1">Total Patients</h6>
              <h2 class="fw-bold">{{ stats.total_patients }}</h2>
            </div>
            <div class="fs-1 opacity-25">👥</div>
          </div>
        </div>
      </div>

    </div>

    <!-- Quick Actions -->
    <div class="row g-3 mb-4">

      <div class="col-12 col-md-6 col-lg-3">
        <router-link to="/doctor/appointments?view=today" class="card text-center text-decoration-none text-dark shadow-sm h-100">
          <div class="card-body">
            <div class="fs-1 mb-2">📅</div>
            <h6 class="fw-semibold">Today's Schedule</h6>
          </div>
        </router-link>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <router-link to="/doctor/appointments" class="card text-center text-decoration-none text-dark shadow-sm h-100">
          <div class="card-body">
            <div class="fs-1 mb-2">🗓️</div>
            <h6 class="fw-semibold">All Appointments</h6>
          </div>
        </router-link>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <router-link to="/doctor/patients" class="card text-center text-decoration-none text-dark shadow-sm h-100">
          <div class="card-body">
            <div class="fs-1 mb-2">👥</div>
            <h6 class="fw-semibold">My Patients</h6>
          </div>
        </router-link>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <router-link to="/doctor/availability" class="card text-center text-decoration-none text-dark shadow-sm h-100">
          <div class="card-body">
            <div class="fs-1 mb-2">⏰</div>
            <h6 class="fw-semibold">Manage Availability</h6>
          </div>
        </router-link>
      </div>

    </div>

    <!-- Today's Appointments Preview -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h5 class="fw-bold mb-3">Today's Appointments</h5>

        <!-- Loading -->
        <div v-if="loadingToday" class="d-flex justify-content-center py-4">
          <div class="spinner-border text-primary"></div>
        </div>

        <!-- Empty -->
        <div v-else-if="todaysAppointments.length === 0" class="text-center text-muted py-4">
          No appointments scheduled for today
        </div>

        <!-- Appointments -->
        <div v-else class="d-flex flex-column gap-2">
          <div
            v-for="apt in todaysAppointments"
            :key="apt.id"
            class="border rounded p-3"
            style="cursor:pointer;"
            @click="$router.push(`/doctor/appointments/${apt.id}`)"
          >
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="fw-semibold mb-1">{{ apt.patient_name }}</h6>
                <p class="text-muted small mb-0">{{ apt.reason || 'General consultation' }}</p>
              </div>

              <div class="text-end">
                <span class="fw-bold text-primary">{{ apt.time }}</span>

                <span
                  class="badge d-block mt-2"
                  :class="{
                    'bg-primary': apt.status === 'Booked',
                    'bg-success': apt.status === 'Completed',
                    'bg-secondary': apt.status !== 'Booked' && apt.status !== 'Completed'
                  }"
                >
                  {{ apt.status }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Link -->
        <router-link
          v-if="todaysAppointments.length > 0"
          to="/doctor/appointments?view=today"
          class="d-block text-center mt-3 text-primary fw-semibold"
        >
          View all today's appointments →
        </router-link>
      </div>
    </div>

    <!-- Extra Page Loading -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

  </div>
</template>