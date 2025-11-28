<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { doctorAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const appointments = ref([])
const selectedAppointment = ref(null)
const showTreatmentForm = ref(false)
const loading = ref(false)
const submitting = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

const filters = ref({
  view: route.query.view || 'upcoming',
  status: '',
  date: ''
})

const treatmentForm = ref({
  diagnosis: '',
  prescription: '',
  notes: '',
  next_visit_date: ''
})

async function loadAppointments(page = 1) {
  loading.value = true
  try {
    const response = await doctorAPI.getAppointments({
      page,
      per_page: 10,
      ...filters.value
    })
    appointments.value = response.data.appointments
    currentPage.value = page
    totalPages.value = response.data.pages
  } catch (error) {
    console.error('Load appointments error:', error)
    messageStore.error('Failed to load appointments')
  } finally {
    loading.value = false
  }
}

async function viewAppointment(apt) {
  try {
    const response = await doctorAPI.getAppointment(apt.id)
    selectedAppointment.value = response.data
  } catch (error) {
    console.error('View appointment error:', error)
    messageStore.error('Failed to load appointment details')
  }
}

async function saveTreatment() {
  submitting.value = true
  try {
    await doctorAPI.addTreatment(selectedAppointment.value.id, treatmentForm.value)
    messageStore.success('Treatment added successfully')
    showTreatmentForm.value = false
    closeModal()
    loadAppointments(currentPage.value)
  } catch (error) {
    console.error('Save treatment error:', error)
    messageStore.error(error.response?.data?.message || 'Failed to save treatment')
  } finally {
    submitting.value = false
  }
}

async function updateStatus(status) {
  try {
    await doctorAPI.updateAppointment(selectedAppointment.value.id, { status })
    messageStore.success(`Appointment ${status}`)
    closeModal()
    loadAppointments(currentPage.value)
  } catch (error) {
    console.error('Update status error:', error)
    messageStore.error('Failed to update appointment')
  }
}

function applyFilters() {
  currentPage.value = 1
  loadAppointments(1)
}

function clearFilters() {
  filters.value = { view: 'upcoming', status: '', date: '' }
  loadAppointments(1)
}

function closeModal() {
  selectedAppointment.value = null
  showTreatmentForm.value = false
  treatmentForm.value = {
    diagnosis: '',
    prescription: '',
    notes: '',
    next_visit_date: ''
  }
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
    <h1 class="h3 fw-bold mb-3">Appointments</h1>

    <!-- View Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row gx-3 gy-2">
          <div class="col-12 col-md-3">
            <select v-model="filters.view" @change="applyFilters" class="form-select">
              <option value="upcoming">Upcoming</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="all">All</option>
            </select>
          </div>

          <div class="col-12 col-md-3">
            <select v-model="filters.status" @change="applyFilters" class="form-select">
              <option value="">All Status</option>
              <option value="booked">Booked</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div class="col-12 col-md-3">
            <input v-model="filters.date" @change="applyFilters" type="date" class="form-control" />
          </div>

          <div class="col-12 col-md-3">
            <button @click="clearFilters" class="btn btn-secondary w-100">Clear Filters</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointments List -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>

    <div v-else-if="appointments.length === 0" class="card text-center p-4 text-muted">
      No appointments found
    </div>

    <div v-else class="row g-3">
      <div
        v-for="apt in appointments"
        :key="apt.id"
        class="col-12"
      >
        <div class="card h-100" role="button" @click="viewAppointment(apt)">
          <div class="card-body d-flex justify-content-between align-items-start">
            <div class="flex-grow-1 me-3">
              <div class="d-flex align-items-center gap-3 mb-2">
                <h5 class="mb-0">{{ apt.patient_name }}</h5>

                <span
                  class="badge"
                  :class="apt.status === 'Booked' ? 'bg-primary' : apt.status === 'Completed' ? 'bg-success' : 'bg-secondary'"
                >
                  {{ apt.status }}
                </span>

                <span v-if="apt.has_treatment" class="badge bg-warning text-dark">
                  Has Treatment
                </span>
              </div>

              <p class="mb-1 text-muted small">{{ apt.patient_age }} years • {{ apt.patient_gender }}</p>
              <p class="mb-0">{{ apt.reason || 'No reason specified' }}</p>
            </div>

            <div class="text-end">
              <div class="h4 text-primary mb-1">{{ apt.time }}</div>
              <div class="small text-muted">{{ formatDate(apt.date) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="d-flex justify-content-center gap-2 mt-4">
      <button
        v-for="page in totalPages"
        :key="page"
        @click="loadAppointments(page)"
        :class="['btn btn-sm', currentPage === page ? 'btn-primary' : 'btn-outline-secondary']"
      >
        {{ page }}
      </button>
    </div>

    <!-- Appointment Details Modal -->
    <div
      v-if="selectedAppointment"
      class="modal d-block"
      tabindex="-1"
      @click.self="closeModal"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details</h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>

          <div class="modal-body">
            <!-- Patient Info -->
            <div class="card mb-4 bg-light">
              <div class="card-body">
                <h6 class="fw-semibold mb-3">Patient Information</h6>
                <div class="row g-3">
                  <div class="col-12 col-md-6">
                    <p class="text-muted mb-1">Name</p>
                    <p class="mb-0">{{ selectedAppointment.patient.name }}</p>
                  </div>
                  <div class="col-12 col-md-6">
                    <p class="text-muted mb-1">Age / Gender</p>
                    <p class="mb-0">{{ selectedAppointment.patient.age }} / {{ selectedAppointment.patient.gender }}</p>
                  </div>
                  <div class="col-12 col-md-6">
                    <p class="text-muted mb-1">Contact</p>
                    <p class="mb-0">{{ selectedAppointment.patient.contact }}</p>
                  </div>
                  <div class="col-12 col-md-6">
                    <p class="text-muted mb-1">Blood Group</p>
                    <p class="mb-0">{{ selectedAppointment.patient.blood_group || 'N/A' }}</p>
                  </div>
                </div>

                <div v-if="selectedAppointment.patient.allergies" class="mt-3 alert alert-danger">
                  <strong>⚠️ Allergies:</strong>
                  <div>{{ selectedAppointment.patient.allergies }}</div>
                </div>
              </div>
            </div>

            <!-- Appointment Info -->
            <div class="mb-4">
              <h6 class="fw-semibold mb-3">Appointment Details</h6>
              <div class="row g-3">
                <div class="col-12 col-md-6">
                  <p class="text-muted mb-1">Date & Time</p>
                  <p class="mb-0">{{ formatDate(selectedAppointment.date) }} at {{ selectedAppointment.time }}</p>
                </div>
                <div class="col-12 col-md-6">
                  <p class="text-muted mb-1">Status</p>
                  <p class="mb-0">
                    <span
                      class="badge"
                      :class="selectedAppointment.status === 'Booked' ? 'bg-primary' : selectedAppointment.status === 'Completed' ? 'bg-success' : 'bg-secondary'"
                    >
                      {{ selectedAppointment.status }}
                    </span>
                  </p>
                </div>
              </div>

              <div v-if="selectedAppointment.reason" class="mt-3">
                <p class="text-muted mb-1">Reason for Visit</p>
                <p class="mb-0">{{ selectedAppointment.reason }}</p>
              </div>
            </div>

            <!-- Treatment Section -->
            <div v-if="selectedAppointment.treatment" class="mb-4 border-top pt-3">
              <h6 class="fw-semibold mb-3">Treatment Record</h6>

              <div class="mb-3">
                <p class="text-muted mb-1">Diagnosis</p>
                <p class="mb-0">{{ selectedAppointment.treatment.diagnosis }}</p>
              </div>

              <div v-if="selectedAppointment.treatment.prescription">
                <p class="text-muted mb-1">Prescription</p>
                <pre class="mb-0">{{ selectedAppointment.treatment.prescription }}</pre>
              </div>

              <div v-if="selectedAppointment.treatment.notes" class="mt-3">
                <p class="text-muted mb-1">Notes</p>
                <p class="mb-0">{{ selectedAppointment.treatment.notes }}</p>
              </div>

              <div v-if="selectedAppointment.treatment.next_visit_date" class="mt-3">
                <p class="text-muted mb-1">Next Visit</p>
                <p class="mb-0">{{ formatDate(selectedAppointment.treatment.next_visit_date) }}</p>
              </div>
            </div>

            <!-- Actions -->
            <div class="d-flex gap-2">
              <button
                v-if="!selectedAppointment.treatment && selectedAppointment.status === 'Booked'"
                @click="showTreatmentForm = true"
                class="btn btn-success me-2"
              >
                Add Treatment & Complete
              </button>

              <button
                v-if="selectedAppointment.status === 'Booked'"
                @click="updateStatus('cancelled')"
                class="btn btn-danger"
              >
                Cancel
              </button>

              <button
                @click="$router.push(`/doctor/patients/${selectedAppointment.patient.id}`)"
                class="btn btn-primary ms-auto"
              >
                View Full History
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Treatment Modal -->
    <div
      v-if="showTreatmentForm"
      class="modal d-block"
      tabindex="-1"
      @click.self="showTreatmentForm = false"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Treatment</h5>
            <button type="button" class="btn-close" @click="showTreatmentForm = false" aria-label="Close"></button>
          </div>

          <form @submit.prevent="saveTreatment">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Diagnosis *</label>
                <textarea v-model="treatmentForm.diagnosis" rows="3" required class="form-control" placeholder="Enter diagnosis..."></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label">Prescription</label>
                <textarea v-model="treatmentForm.prescription" rows="4" class="form-control" placeholder="Medications, dosage, instructions..."></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea v-model="treatmentForm.notes" rows="3" class="form-control" placeholder="Additional notes..."></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label">Next Visit Date</label>
                <input v-model="treatmentForm.next_visit_date" type="date" class="form-control" />
              </div>
            </div>

            <div class="modal-footer">
              <button type="submit" :disabled="submitting" class="btn btn-success">
                {{ submitting ? 'Saving...' : 'Save Treatment & Complete' }}
              </button>
              <button type="button" class="btn btn-secondary" @click="showTreatmentForm = false">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
