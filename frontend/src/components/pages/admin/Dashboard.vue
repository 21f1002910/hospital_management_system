<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '../../../services/api'
import { useRouter } from 'vue-router'
import { useMessageStore } from '../../../store'

const router = useRouter()
const messageStore = useMessageStore()

const stats = ref({
  total_doctors: 0,
  total_patients: 0,
  total_appointments: 0,
  todays_appointments: 0,
  upcoming_appointments: 0,
  recent_appointments: 0
})

const loading = ref(false)

async function loadDashboard() {
  loading.value = true
  try {
    const response = await adminAPI.getDashboard()
    stats.value = response.data
  } catch (error) {
    messageStore.error('Failed to load dashboard data')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<template>
  <div class="container my-4">
    <h1 class="h3 fw-bold mb-4">Admin Dashboard</h1>

    <!-- Statistics Cards -->
    <div class="row g-3 mb-4">
      <div class="col-12 col-md-6 col-lg-4">
        <div class="card text-white bg-primary h-100">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <div class="small">Total Doctors</div>
              <div class="fs-2 fw-bold">{{ stats.total_doctors }}</div>
            </div>
            <div class="fs-1 text-white-50">👨‍⚕️</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card text-white bg-success h-100">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <div class="small">Total Patients</div>
              <div class="fs-2 fw-bold">{{ stats.total_patients }}</div>
            </div>
            <div class="fs-1 text-white-50">🏥</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card text-white bg-secondary h-100">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <div class="small">Total Appointments</div>
              <div class="fs-2 fw-bold">{{ stats.total_appointments }}</div>
            </div>
            <div class="fs-1 text-white-50">📅</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card text-white bg-warning h-100">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <div class="small">Today's Appointments</div>
              <div class="fs-2 fw-bold">{{ stats.todays_appointments }}</div>
            </div>
            <div class="fs-1 text-white-50">🗓️</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card text-white bg-danger h-100">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <div class="small">Upcoming</div>
              <div class="fs-2 fw-bold">{{ stats.upcoming_appointments }}</div>
            </div>
            <div class="fs-1 text-white-50">⏰</div>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card text-white bg-info h-100">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <div class="small">Recent (7 days)</div>
              <div class="fs-2 fw-bold">{{ stats.recent_appointments }}</div>
            </div>
            <div class="fs-1 text-white-50">📊</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row g-3 mb-4">
      <div class="col-12 col-md-6 col-lg-3">
        <router-link :to="{ name:'AdminDoctors'}" class="card h-100 text-decoration-none text-body">
          <div class="card-body text-center">
            <div class="fs-2 mb-2">👨‍⚕️</div>
            <h5 class="card-title mb-0">Manage Doctors</h5>
          </div>
        </router-link>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <router-link :to="{name:'AdminPatients'}" class="card h-100 text-decoration-none text-body">
          <div class="card-body text-center">
            <div class="fs-2 mb-2">🏥</div>
            <h5 class="card-title mb-0">View Patients</h5>
          </div>
        </router-link>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <router-link :to="{name:'AdminAppointments'}" class="card h-100 text-decoration-none text-body">
          <div class="card-body text-center">
            <div class="fs-2 mb-2">📅</div>
            <h5 class="card-title mb-0">Appointments</h5>
          </div>
        </router-link>
      </div>

      <div class="col-12 col-md-6 col-lg-3">
        <router-link :to="{ name:'AdminDepartments'}" class="card h-100 text-decoration-none text-body">
          <div class="card-body text-center">
            <div class="fs-2 mb-2">🏢</div>
            <h5 class="card-title mb-0">Departments</h5>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Loading (reusable) -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>
