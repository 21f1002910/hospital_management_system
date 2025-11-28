<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '../../../services/api'
import { useMessageStore } from '../../../store'

const messageStore = useMessageStore()

const patients = ref([])
const selectedPatient = ref(null)
const searchQuery = ref('')
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

async function loadPatients(page = 1) {
  loading.value = true
  try {
    const response = await adminAPI.getPatients({ 
      page, 
      per_page: 10,
      search: searchQuery.value 
    })
    patients.value = response.data.patients
    currentPage.value = page
    totalPages.value = response.data.pages
  } catch (error) {
    console.error('Load patients error:', error)
    messageStore.error('Failed to load patients')
  } finally {
    loading.value = false
  }
}

async function searchPatients() {
  currentPage.value = 1
  await loadPatients(1)
}

function clearSearch() {
  searchQuery.value = ''
  loadPatients(1)
}

async function viewPatient(id) {
  try {
    const response = await adminAPI.getPatient(id)
    selectedPatient.value = response.data
  } catch (error) {
    console.error('View patient error:', error)
    messageStore.error('Failed to load patient details')
  }
}

onMounted(() => {
  loadPatients()
})
</script>

<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0">Patients</h1>
    </div>

    <!-- Search Bar -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="d-flex gap-2">
          <input
            v-model="searchQuery"
            @keyup.enter="searchPatients"
            type="text"
            placeholder="Search by name, email, ID, or contact..."
            class="form-control"
          />
          <button @click="searchPatients" class="btn btn-primary">Search</button>
          <button @click="clearSearch" class="btn btn-secondary">Clear</button>
        </div>
      </div>
    </div>

    <!-- Patients Table -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
          <div class="spinner-border" role="status" aria-hidden="true"></div>
          <span class="visually-hidden">Loading...</span>
        </div>

        <div v-else-if="patients.length === 0" class="text-center py-5 text-muted">
          No patients found
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Contact</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in patients" :key="patient.id">
                <td class="align-middle">{{ patient.id }}</td>
                <td class="align-middle fw-medium">{{ patient.name }}</td>
                <td class="align-middle text-muted">{{ patient.email }}</td>
                <td class="align-middle">{{ patient.age || 'N/A' }}</td>
                <td class="align-middle">{{ patient.gender || 'N/A' }}</td>
                <td class="align-middle">{{ patient.contact || 'N/A' }}</td>
                <td class="align-middle">
                  <button @click="viewPatient(patient.id)" class="btn btn-link btn-sm text-primary">View Details</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="d-flex justify-content-center gap-2 mt-3">
      <button
        v-for="page in totalPages"
        :key="page"
        @click="loadPatients(page)"
        :class="['btn btn-sm', currentPage === page ? 'btn-primary' : 'btn-outline-secondary']"
      >
        {{ page }}
      </button>
    </div>

    <!-- Patient Details Modal -->
    <div
      v-if="selectedPatient"
      class="modal d-block"
      tabindex="-1"
      @click.self="selectedPatient = null"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Patient Details</h5>
            <button type="button" class="btn-close" @click="selectedPatient = null" aria-label="Close"></button>
          </div>

          <div class="modal-body">
            <div class="row g-3 mb-3">
              <div class="col-12 col-md-6">
                <p class="text-muted mb-1">Name</p>
                <p class="fw-medium mb-0">{{ selectedPatient.name }}</p>
              </div>

              <div class="col-12 col-md-6">
                <p class="text-muted mb-1">Email</p>
                <p class="fw-medium mb-0">{{ selectedPatient.email }}</p>
              </div>

              <div class="col-12 col-md-6">
                <p class="text-muted mb-1">Age</p>
                <p class="fw-medium mb-0">{{ selectedPatient.age || 'N/A' }}</p>
              </div>

              <div class="col-12 col-md-6">
                <p class="text-muted mb-1">Gender</p>
                <p class="fw-medium mb-0">{{ selectedPatient.gender || 'N/A' }}</p>
              </div>

              <div class="col-12 col-md-6">
                <p class="text-muted mb-1">Contact</p>
                <p class="fw-medium mb-0">{{ selectedPatient.contact || 'N/A' }}</p>
              </div>

              <div class="col-12 col-md-6">
                <p class="text-muted mb-1">Blood Group</p>
                <p class="fw-medium mb-0">{{ selectedPatient.blood_group || 'N/A' }}</p>
              </div>

              <div class="col-12">
                <p class="text-muted mb-1">Address</p>
                <p class="fw-medium mb-0">{{ selectedPatient.address || 'N/A' }}</p>
              </div>
            </div>

            <div v-if="selectedPatient.allergies" class="alert alert-danger">
              <strong>⚠️ Allergies</strong>
              <div class="mt-2">{{ selectedPatient.allergies }}</div>
            </div>

            <div class="mt-4">
              <h6 class="fw-semibold">Appointment History</h6>

              <div v-if="selectedPatient.appointments?.length > 0" class="mt-3">
                <div v-for="apt in selectedPatient.appointments" :key="apt.id" class="card mb-2">
                  <div class="card-body d-flex justify-content-between align-items-start">
                    <div>
                      <p class="mb-1 fw-medium">{{ apt.doctor_name }}</p>
                      <p class="mb-0 text-muted small">{{ apt.doctor_specialization }}</p>
                    </div>
                    <div class="text-end">
                      <p class="mb-1 small">{{ apt.date }} {{ apt.time }}</p>
                      <span
                        class="badge"
                        :class="apt.status === 'Booked' ? 'bg-primary' : apt.status === 'Completed' ? 'bg-success' : 'bg-secondary'"
                      >
                        {{ apt.status }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="text-center text-muted mt-3">
                No appointments found
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="selectedPatient = null">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
