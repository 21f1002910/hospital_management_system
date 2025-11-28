<script setup>
import { ref, computed, onMounted } from 'vue'
import { doctorAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const messageStore = useMessageStore()

const patients = ref([])
const loading = ref(false)
const searchQuery = ref('')

const filteredPatients = computed(() => {
  if (!searchQuery.value) return patients.value
  
  const query = searchQuery.value.toLowerCase()
  return patients.value.filter(p => 
    p.name.toLowerCase().includes(query) ||
    p.contact.toLowerCase().includes(query)
  )
})

const maleCount = computed(() => {
  return patients.value.filter(p => p.gender?.toLowerCase() === 'male').length
})

const femaleCount = computed(() => {
  return patients.value.filter(p => p.gender?.toLowerCase() === 'female').length
})

function getInitials(name) {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

async function loadPatients() {
  loading.value = true
  try {
    const response = await doctorAPI.getPatients()
    patients.value = response.data.patients
  } catch (error) {
    console.error('Load patients error:', error)
    messageStore.error('Failed to load patients')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPatients()
})
</script>

<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0">My Patients</h1>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="patients.length === 0" class="card text-center p-5 text-muted">
      <div class="display-1 mb-3">👥</div>
      <h4 class="mb-2">No patients assigned yet</h4>
      <p class="mb-0">Patients will appear here once they book appointments with you</p>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Summary Stats -->
      <div class="row g-3 mb-4">
        <div class="col-12 col-md-4">
          <div class="card h-100">
            <div class="card-body">
              <div class="small text-muted">Total Patients</div>
              <div class="h3 text-primary fw-bold">{{ patients.length }}</div>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-4">
          <div class="card h-100">
            <div class="card-body">
              <div class="small text-muted">Male Patients</div>
              <div class="h3 text-success fw-bold">{{ maleCount }}</div>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-4">
          <div class="card h-100">
            <div class="card-body">
              <div class="small text-muted">Female Patients</div>
              <div class="h3 text-danger fw-bold">{{ femaleCount }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Search Bar -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="input-group">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search patients by name..."
              class="form-control"
            />
            <button class="btn btn-outline-secondary" @click="searchPatients">Search</button>
            <button class="btn btn-secondary" @click="clearSearch">Clear</button>
          </div>
        </div>
      </div>

      <!-- Patients Grid -->
      <div class="row g-4">
        <div
          v-for="patient in filteredPatients"
          :key="patient.id"
          class="col-12 col-md-6 col-lg-4"
        >
          <div class="card h-100" role="button" @click="$router.push(`/doctor/patients/${patient.id}`)">
            <div class="card-body d-flex flex-column">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <div class="d-flex align-items-center gap-3">
                  <div
                    class="rounded-circle d-flex align-items-center justify-content-center text-white"
                    :style="{ width: '64px', height: '64px', background: '#0d6efd', fontWeight: '700' }"
                  >
                    {{ getInitials(patient.name) }}
                  </div>
                  <div>
                    <h5 class="mb-0">{{ patient.name }}</h5>
                    <div class="small text-muted">{{ patient.age }} years • {{ patient.gender }}</div>
                  </div>
                </div>

                <span class="badge bg-light text-primary">
                  {{ patient.appointment_count }} {{ patient.appointment_count === 1 ? 'visit' : 'visits' }}
                </span>
              </div>

              <div class="mt-auto">
                <p class="mb-2"><span class="me-2">📞</span>{{ patient.contact }}</p>

                <div class="pt-3 border-top">
                  <button
                    class="btn btn-primary w-100"
                    @click.stop="$router.push(`/doctor/patients/${patient.id}`)"
                  >
                    View Full History →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
