<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { patientAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const router = useRouter()
const messageStore = useMessageStore()

const appointments = ref([])
const view = ref('upcoming')
const loading = ref(false)
const submitting = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

const reschedulingApt = ref(null)
const cancellingApt = ref(null)

const rescheduleForm = ref({
  date: '',
  time: ''
})

const viewOptions = [
  { value: 'upcoming', label: 'Upcoming' },
  { value: 'past', label: 'Past' },
  { value: 'all', label: 'All' }
]

const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

async function loadAppointments(page = 1) {
  loading.value = true
  try {
    const response = await patientAPI.getAppointments({
      view: view.value,
      page,
      per_page: 10
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

function changeView(newView) {
  view.value = newView
  currentPage.value = 1
  loadAppointments(1)
}

function viewDetails(id) {
  router.push(`/patient/appointments/${id}`)
}

function openRescheduleModal(apt) {
  reschedulingApt.value = apt
  rescheduleForm.value = {
    date: apt.date,
    time: apt.time
  }
}

function closeRescheduleModal() {
  reschedulingApt.value = null
  rescheduleForm.value = { date: '', time: '' }
}

async function rescheduleAppointment() {
  submitting.value = true
  try {
    await patientAPI.rescheduleAppointment(reschedulingApt.value.id, rescheduleForm.value)
    messageStore.success('Appointment rescheduled successfully')
    closeRescheduleModal()
    loadAppointments(currentPage.value)
  } catch (error) {
    console.error('Reschedule error:', error)
    messageStore.error(error.response?.data?.message || 'Failed to reschedule appointment')
  } finally {
    submitting.value = false
  }
}

function confirmCancel(apt) {
  cancellingApt.value = apt
}

async function cancelAppointment() {
  submitting.value = true
  try {
    await patientAPI.cancelAppointment(cancellingApt.value.id)
    messageStore.success('Appointment cancelled successfully')
    cancellingApt.value = null
    loadAppointments(currentPage.value)
  } catch (error) {
    console.error('Cancel error:', error)
    messageStore.error('Failed to cancel appointment')
  } finally {
    submitting.value = false
  }
}

function getEmptyMessage() {
  if (view.value === 'upcoming') return 'You have no upcoming appointments'
  if (view.value === 'past') return 'You have no past appointments'
  return 'You have not booked any appointments yet'
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

function getDayOfWeek(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { weekday: 'long' })
}

function formatTime(time) {
  const [hours, minutes] = time.split(':')
  const hour = parseInt(hours)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const displayHour = hour % 12 || 12
  return `${displayHour}:${minutes} ${ampm}`
}

onMounted(() => {
  loadAppointments()
})
</script>


<template>
  <div class="container my-4">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h4 mb-0">My Appointments</h1>
      <router-link to="/patient/doctors" class="btn btn-success">
        + Book New Appointment
      </router-link>
    </div>

    <!-- View Filter -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="btn-group" role="group" aria-label="View options">
          <button
            v-for="option in viewOptions"
            :key="option.value"
            @click="changeView(option.value)"
            :class="['btn', view === option.value ? 'btn-primary' : 'btn-outline-secondary']"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="appointments.length === 0" class="card text-center p-4 text-muted mb-4">
      <div class="display-1 mb-3">📅</div>
      <h5 class="fw-semibold mb-2">No appointments found</h5>
      <p class="mb-3">{{ getEmptyMessage() }}</p>
      <router-link to="/patient/doctors" class="btn btn-primary">Book an Appointment</router-link>
    </div>

    <!-- Appointments List -->
    <div v-else class="row g-3">
      <div v-for="apt in appointments" :key="apt.id" class="col-12">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div class="me-3 flex-grow-1">
                <div class="d-flex align-items-center mb-2 gap-3">
                  <h5 class="mb-0">{{ apt.doctor_name }}</h5>

                  <span
                    class="badge"
                    :class="apt.status === 'Booked' ? 'bg-primary' : apt.status === 'Completed' ? 'bg-success' : apt.status === 'Cancelled' ? 'bg-danger' : 'bg-secondary'"
                  >
                    {{ apt.status }}
                  </span>

                  <span v-if="apt.has_treatment" class="badge bg-warning text-dark">Has Treatment</span>
                </div>

                <div class="text-primary fw-medium mb-2">{{ apt.doctor_specialization }}</div>

                <p class="mb-1"><strong>Date:</strong> {{ formatDate(apt.date) }}</p>
                <p class="mb-2"><strong>Time:</strong> {{ formatTime(apt.time) }}</p>
                <p v-if="apt.reason" class="mb-0"><strong>Reason:</strong> {{ apt.reason }}</p>
              </div>

              <div class="text-end">
                <div class="h3 text-primary mb-1">{{ formatTime(apt.time) }}</div>
                <div class="small text-muted">{{ getDayOfWeek(apt.date) }}</div>
              </div>
            </div>

            <!-- Actions -->
            <div class="d-flex gap-2 mt-3 border-top pt-3">
              <button @click="viewDetails(apt.id)" class="btn btn-primary flex-grow-1">View Details</button>

              <button
                v-if="apt.status === 'Booked'"
                @click="openRescheduleModal(apt)"
                class="btn btn-warning"
              >
                Reschedule
              </button>

              <button
                v-if="apt.status === 'Booked'"
                @click="confirmCancel(apt)"
                class="btn btn-danger"
              >
                Cancel
              </button>
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

    <!-- Reschedule Modal -->
    <div
      v-if="reschedulingApt"
      class="modal d-block"
      tabindex="-1"
      @click.self="closeRescheduleModal"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reschedule Appointment</h5>
            <button type="button" class="btn-close" @click="closeRescheduleModal" aria-label="Close"></button>
          </div>

          <form @submit.prevent="rescheduleAppointment">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">New Date</label>
                <input v-model="rescheduleForm.date" type="date" required :min="today" class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">New Time</label>
                <input v-model="rescheduleForm.time" type="time" required class="form-control" />
              </div>

              <div class="small text-muted">Note: Please check doctor's availability before rescheduling</div>
            </div>

            <div class="modal-footer">
              <button type="submit" :disabled="submitting" class="btn btn-primary">
                {{ submitting ? 'Rescheduling...' : 'Confirm' }}
              </button>
              <button type="button" class="btn btn-secondary" @click="closeRescheduleModal">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Cancel Confirmation Modal -->
    <div
      v-if="cancellingApt"
      class="modal d-block"
      tabindex="-1"
      @click.self="cancellingApt = null"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Cancel Appointment</h5>
            <button type="button" class="btn-close" @click="cancellingApt = null" aria-label="Close"></button>
          </div>

          <div class="modal-body">
            <p>
              Are you sure you want to cancel your appointment with
              <strong>{{ cancellingApt.doctor_name }}</strong> on
              <strong>{{ formatDate(cancellingApt.date) }}</strong>?
            </p>
          </div>

          <div class="modal-footer">
            <button @click="cancelAppointment" :disabled="submitting" class="btn btn-danger">
              {{ submitting ? 'Cancelling...' : 'Yes, Cancel' }}
            </button>
            <button @click="cancellingApt = null" class="btn btn-secondary">No, Keep It</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
