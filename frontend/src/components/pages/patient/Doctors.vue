<script setup>
import { ref, onMounted } from 'vue'
import { patientAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const messageStore = useMessageStore()

const doctors = ref([])
const departments = ref([])
const searchQuery = ref('')
const specializationFilter = ref('')
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const total = ref(0)

async function loadDoctors(page = 1) {
  loading.value = true
  try {
    const response = await patientAPI.getDoctors({
      page,
      per_page: 12,
      search: searchQuery.value,
      specialization: specializationFilter.value
    })
    doctors.value = response.data.doctors
    currentPage.value = page
    totalPages.value = response.data.pages
    total.value = response.data.total
  } catch (error) {
    console.error('Load doctors error:', error)
    messageStore.error('Failed to load doctors')
  } finally {
    loading.value = false
  }
}

async function loadDepartments() {
  try {
    const response = await patientAPI.getDepartments()
    departments.value = response.data.departments
  } catch (error) {
    console.error('Load departments error:', error)
  }
}

function searchDoctors() {
  currentPage.value = 1
  loadDoctors(1)
}

function clearFilters() {
  searchQuery.value = ''
  specializationFilter.value = ''
  loadDoctors(1)
}

function getInitials(name) {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

onMounted(() => {
  loadDoctors()
  loadDepartments()
})
</script>


<template>
  <div class="container my-4">
    <h1 class="h3 fw-bold mb-3">Find a Doctor</h1>

    <!-- Search and Filter -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-12 col-md-5">
            <input
              v-model="searchQuery"
              @keyup.enter="searchDoctors"
              type="text"
              placeholder="Search by doctor name..."
              class="form-control"
            />
          </div>

          <div class="col-12 col-md-4">
            <select
              v-model="specializationFilter"
              @change="searchDoctors"
              class="form-select"
            >
              <option value="">All Specializations</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                {{ dept.name }}
              </option>
            </select>
          </div>

          <div class="col-12 col-md-3 d-flex gap-2">
            <button @click="searchDoctors" class="btn btn-primary flex-fill">Search</button>
            <button @click="clearFilters" class="btn btn-secondary flex-fill">Clear</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>

    <!-- No Results -->
    <div v-else-if="doctors.length === 0" class="card text-center p-5 text-muted">
      <div class="display-1 mb-3">👨‍⚕️</div>
      <h5 class="fw-semibold mb-2">No doctors found</h5>
      <p class="mb-0">Try adjusting your search or filters</p>
    </div>

    <!-- Doctors Grid -->
    <div v-else>
      <p class="text-muted mb-3">Found {{ total }} doctors</p>

      <div class="row g-4">
        <div
          v-for="doctor in doctors"
          :key="doctor.id"
          class="col-12 col-md-6 col-lg-4"
        >
          <div class="card h-100" role="button" @click="$router.push(`/patient/doctors/${doctor.id}`)">
            <!-- Doctor Header -->
            <div class="card-header text-white" style="background: linear-gradient(90deg,#0d6efd,#0b5ed7);">
              <div class="d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center gap-3">
                  <div class="rounded-circle bg-white bg-opacity-25 d-flex align-items-center justify-content-center text-white" style="width:56px; height:56px;">
                    {{ getInitials(doctor.name) }}
                  </div>
                  <div>
                    <h5 class="mb-0 text-white">{{ doctor.name }}</h5>
                  </div>
                </div>
              </div>
            </div>

            <!-- Doctor Info -->
            <div class="card-body d-flex flex-column">
              <div class="mb-3">
                <div class="text-primary fw-semibold">
                  <span class="me-2"></span>{{ doctor.specialization }}
                </div>
              </div>

              <p class="text-muted small flex-grow-1 mb-3">
                {{ doctor.bio || 'Experienced medical professional dedicated to patient care.' }}
              </p>

              <div v-if="doctor.contact" class="text-muted small mb-3">
                <span class="me-2">📞</span>{{ doctor.contact }}
              </div>

              <button
                @click.stop="$router.push(`/patient/doctors/${doctor.id}`)"
                class="btn btn-primary mt-auto"
              >
                View Profile &amp; Book
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="d-flex justify-content-center gap-2 mt-4">
        <button
          v-for="page in totalPages"
          :key="page"
          @click="loadDoctors(page)"
          :class="['btn btn-sm', currentPage === page ? 'btn-primary' : 'btn-outline-secondary']"
        >
          {{ page }}
        </button>
      </div>
    </div>
  </div>
</template>
