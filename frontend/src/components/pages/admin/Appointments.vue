<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '../../../services/api'
import { useMessageStore } from '../../../store'

const messageStore = useMessageStore()

const appointments = ref([])
const selectedAppointment = ref(null)
const editingAppointment = ref(null)
const loading = ref(false)
const submitting = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

const filters = ref({
  status: '',
  date: ''
})

const editForm = ref({
  status: '',
  notes: ''
})

async function loadAppointments(page = 1) {
  loading.value = true
  try {
    const params = {
      page,
      per_page: 10,
      ...filters.value
    }
    const response = await adminAPI.getAppointments(params)
    appointments.value = response.data.appointments
    currentPage.value = page
    totalPages.value = response.data.pages
  } catch (error) {
    messageStore.error('Failed to load appointments')
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  currentPage.value = 1
  loadAppointments(1)
}

function clearFilters() {
  filters.value = { status: '', date: '' }
  loadAppointments(1)
}

async function viewAppointment(apt) {
  try {
    const response = await adminAPI.getAppointment(apt.id)
    selectedAppointment.value = response.data
  } catch (error) {
    messageStore.error('Failed to load appointment details')
  }
}

function editAppointment(apt) {
  editingAppointment.value = apt
  editForm.value = {
    status: apt.status.toLowerCase(),
    notes: apt.notes || ''
  }
}

async function saveAppointment() {
  submitting.value = true
  try {
    await adminAPI.updateAppointment(editingAppointment.value.id, editForm.value)
    messageStore.success('Appointment updated successfully')
    closeEditModal()
    loadAppointments(currentPage.value)
  } catch (error) {
    messageStore.error('Failed to update appointment')
  } finally {
    submitting.value = false
  }
}

function closeEditModal() {
  editingAppointment.value = null
  editForm.value = { status: '', notes: '' }
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(() => {
  loadAppointments()
})
</script>

<template>
  <div class="container my-4">
    <h1 class="h3 fw-bold mb-4">Appointments Management</h1>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row gy-2 gx-3 align-items-center">
          <div class="col-12 col-md-3">
            <select v-model="filters.status" @change="applyFilters" class="form-select">
              <option value="">All Status</option>
              <option value="booked">Booked</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div class="col-12 col-md-3">
            <input
              v-model="filters.date"
              @change="applyFilters"
              type="date"
              class="form-control"
            />
          </div>

          <div class="col-6 col-md-3">
            <button @click="applyFilters" class="btn btn-primary w-100">Apply Filters</button>
          </div>

          <div class="col-6 col-md-3">
            <button @click="clearFilters" class="btn btn-secondary w-100">Clear Filters</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointments Table -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
          <div class="spinner-border" role="status" aria-hidden="true"></div>
          <span class="visually-hidden">Loading...</span>
        </div>

        <div v-else-if="appointments.length === 0" class="text-center py-5 text-muted">
          No appointments found
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Specialization</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="apt in appointments" :key="apt.id">
                <td class="align-middle">{{ apt.id }}</td>
                <td class="align-middle fw-medium">{{ apt.patient_name }}</td>
                <td class="align-middle">{{ apt.doctor_name }}</td>
                <td class="align-middle text-muted">{{ apt.doctor_specialization }}</td>
                <td class="align-middle">{{ formatDate(apt.date) }}</td>
                <td class="align-middle">{{ apt.time }}</td>
                <td class="align-middle">
                  <span
                    class="badge"
                    :class="apt.status === 'Booked' ? 'bg-primary' : apt.status === 'Completed' ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ apt.status }}
                  </span>
                </td>

                <td class="align-middle">
                  <button @click="viewAppointment(apt)" class="btn btn-link btn-sm text-primary me-2">View</button>
                  <button @click="editAppointment(apt)" class="btn btn-link btn-sm text-success">Edit</button>
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
        @click="loadAppointments(page)"
        :class="['btn btn-sm', currentPage === page ? 'btn-primary' : 'btn-outline-secondary']"
      >
        {{ page }}
      </button>
    </div>

    <!-- View Appointment Modal -->
    <div
      v-if="selectedAppointment"
      class="modal d-block"
      tabindex="-1"
      @click.self="selectedAppointment = null"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details</h5>
            <button type="button" class="btn-close" @click="selectedAppointment = null" aria-label="Close"></button>
          </div>

          <div class="modal-body">
            <div class="row">
              <div class="col-12 col-md-6 mb-3">
                <h6 class="fw-semibold">Patient Information</h6>
                <p class="mb-1"><strong>Name:</strong> {{ selectedAppointment.patient.name }}</p>
                <p class="mb-1"><strong>Age:</strong> {{ selectedAppointment.patient.age }}</p>
                <p class="mb-1"><strong>Gender:</strong> {{ selectedAppointment.patient.gender }}</p>
                <p class="mb-0"><strong>Contact:</strong> {{ selectedAppointment.patient.contact }}</p>
              </div>

              <div class="col-12 col-md-6 mb-3">
                <h6 class="fw-semibold">Doctor Information</h6>
                <p class="mb-1"><strong>Name:</strong> {{ selectedAppointment.doctor.name }}</p>
                <p class="mb-0"><strong>Specialization:</strong> {{ selectedAppointment.doctor.specialization }}</p>
              </div>
            </div>

            <hr />

            <div>
              <h6 class="fw-semibold">Appointment Details</h6>
              <p class="mb-1"><strong>Date:</strong> {{ formatDate(selectedAppointment.date) }}</p>
              <p class="mb-1"><strong>Time:</strong> {{ selectedAppointment.time }}</p>
              <p class="mb-1"><strong>Status:</strong> {{ selectedAppointment.status }}</p>
              <p v-if="selectedAppointment.notes" class="mb-0"><strong>Notes:</strong> {{ selectedAppointment.notes }}</p>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="selectedAppointment = null">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Appointment Modal -->
    <div
      v-if="editingAppointment"
      class="modal d-block"
      tabindex="-1"
      @click.self="closeEditModal"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Appointment</h5>
            <button type="button" class="btn-close" @click="closeEditModal" aria-label="Close"></button>
          </div>

          <form @submit.prevent="saveAppointment">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Status</label>
                <select v-model="editForm.status" required class="form-select">
                  <option value="booked">Booked</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea v-model="editForm.notes" rows="3" class="form-control"></textarea>
              </div>
            </div>

            <div class="modal-footer">
              <button type="submit" :disabled="submitting" class="btn btn-primary">
                {{ submitting ? 'Saving...' : 'Save Changes' }}
              </button>
              <button type="button" class="btn btn-secondary" @click="closeEditModal">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
