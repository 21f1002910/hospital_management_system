<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { patientAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const doctor = ref(null)
const loading = ref(false)
const submitting = ref(false)

const bookingForm = ref({
  date: '',
  time: '',
  reason: ''
})

const availableSlots = computed(() => {
  if (!bookingForm.value.date || !doctor.value) return []
  const availability = doctor.value.availability.find(av => av.date === bookingForm.value.date)
  return availability ? availability.time_slots : []
})

async function loadDoctor() {
  loading.value = true
  try {
    const response = await patientAPI.getDoctor(route.params.id)
    doctor.value = response.data
  } catch (error) {
    console.error('Load doctor error:', error)
    messageStore.error('Failed to load doctor details')
    router.push('/patient/doctors')
  } finally {
    loading.value = false
  }
}

function selectDate(availability) {
  bookingForm.value.date = availability.date
  bookingForm.value.time = '' // Reset time when date changes
}

async function bookAppointment() {
  if (!bookingForm.value.date || !bookingForm.value.time) {
    messageStore.error('Please select both date and time')
    return
  }

  submitting.value = true
  try {
    await patientAPI.bookAppointment({
      doctor_id: doctor.value.id,
      date: bookingForm.value.date,
      time: bookingForm.value.time,
      reason: bookingForm.value.reason
    })
    messageStore.success('Appointment booked successfully! 🎉')
    router.push('/patient/appointments')
  } catch (error) {
    console.error('Book appointment error:', error)
    messageStore.error(error.response?.data?.message || 'Failed to book appointment')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  bookingForm.value = {
    date: '',
    time: '',
    reason: ''
  }
}

function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  if (date.toDateString() === today.toDateString()) {
    return 'Today'
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return 'Tomorrow'
  } else {
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
  }
}

function formatFullDate(dateStr) {
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

onMounted(() => {
  loadDoctor()
})
</script>


<template>
  <div>
    <!-- Back button -->
    <button
      @click="$router.back()"
      class="mb-3 btn btn-link p-0 d-inline-flex align-items-center text-primary fw-medium text-decoration-none"
    >
      <span class="me-2">←</span> Back to Doctors
    </button>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="doctor">
      <!-- Doctor Info Card -->
      <div class="bg-gradient-blue rounded shadow-lg p-4 p-md-5 mb-4 text-white">
        <div class="d-flex flex-column flex-md-row align-items-start justify-content-between">
          <div class="d-flex align-items-center mb-3 mb-md-0">
            <div
              class="d-flex align-items-center justify-content-center rounded-circle bg-white bg-opacity-25 text-uppercase fw-bold me-4"
              style="width: 96px; height: 96px; font-size: 2.25rem;"
            >
              {{ getInitials(doctor.name) }}
            </div>
            <div>
              <h1 class="h2 fw-bold mb-2">Dr. {{ doctor.name }}</h1>
              <p class="h5 text-light mb-1">{{ doctor.specialization }}</p>
              <p v-if="doctor.contact" class="text-light d-flex align-items-center mb-0">
                <span class="me-2">📞</span>{{ doctor.contact }}
              </p>
            </div>
          </div>
          <div class="display-4 opacity-25 d-none d-md-block">👨‍⚕️</div>
        </div>

        <div v-if="doctor.bio" class="mt-4 pt-3 border-top border-light border-opacity-50">
          <p class="fs-6 text-light mb-0">{{ doctor.bio }}</p>
        </div>

        <div v-if="doctor.schedule" class="mt-3">
          <p class="small text-light-50 mb-1">Schedule:</p>
          <p class="mb-0 text-light">{{ doctor.schedule }}</p>
        </div>
      </div>

      <!-- Booking Section -->
      <div class="row g-4">
        <!-- Availability Calendar -->
        <div class="col-12 col-lg-8">
          <div class="bg-white rounded shadow p-4">
            <h2 class="h4 fw-bold text-dark mb-4 d-flex align-items-center">
              <span class="me-2">📅</span>
              Book an Appointment
            </h2>

            <div
              v-if="doctor.availability.length === 0"
              class="text-center py-5 text-muted"
            >
              <div class="display-4 mb-3">📅</div>
              <p class="h5 fw-semibold mb-2">No availability set</p>
              <p class="small mb-0">
                This doctor hasn't set their availability yet. Please check back later or contact the clinic.
              </p>
            </div>

            <div v-else>
              <!-- Date Selection -->
              <div class="mb-4">
                <label class="form-label fw-medium">
                  Select Date <span class="text-danger">*</span>
                </label>
                <div class="row g-3">
                  <div
                    v-for="av in doctor.availability"
                    :key="av.date"
                    class="col-6 col-md-4"
                  >
                    <button
                      type="button"
                      @click="selectDate(av)"
                      :class="[
                        'w-100 text-start rounded border border-2 p-3 btn-date',
                        bookingForm.date === av.date
                          ? 'border-primary bg-light shadow-sm'
                          : 'border-secondary bg-white'
                      ]"
                    >
                      <p class="fw-semibold text-dark mb-1">{{ formatDate(av.date) }}</p>
                      <p class="small text-muted mb-0">
                        {{ av.time_slots.length }} slots available
                      </p>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Time Slot Selection -->
              <div v-if="bookingForm.date" class="mb-4">
                <label class="form-label fw-medium">
                  Select Time <span class="text-danger">*</span>
                </label>
                <div class="row g-3">
                  <div
                    v-for="slot in availableSlots"
                    :key="slot"
                    class="col-4 col-md-3"
                  >
                    <button
                      type="button"
                      @click="bookingForm.time = slot"
                      :class="[
                        'btn w-100 fw-medium py-2',
                        bookingForm.time === slot
                          ? 'btn-primary shadow-sm'
                          : 'btn-outline-secondary'
                      ]"
                    >
                      {{ formatTime(slot) }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Reason -->
              <div class="mb-4">
                <label class="form-label fw-medium">
                  Reason for Visit
                  <span class="text-muted">(Optional but recommended)</span>
                </label>
                <textarea
                  v-model="bookingForm.reason"
                  rows="3"
                  class="form-control"
                  placeholder="Briefly describe your symptoms or reason for consultation..."
                ></textarea>
                <p class="form-text">
                  This helps the doctor prepare for your visit
                </p>
              </div>

              <!-- Book Buttons -->
              <div class="d-flex flex-column flex-md-row gap-2">
                <button
                  @click="bookAppointment"
                  :disabled="!bookingForm.date || !bookingForm.time || submitting"
                  class="btn btn-success flex-fill py-3 fw-semibold fs-6 shadow"
                >
                  {{ submitting ? 'Booking...' : '✓ Confirm Booking' }}
                </button>
                <button
                  @click="resetForm"
                  :disabled="!bookingForm.date && !bookingForm.time"
                  class="btn btn-outline-secondary flex-fill py-3 fw-medium"
                >
                  Clear
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Booking Summary -->
        <div class="col-12 col-lg-4">
          <div class="bg-light rounded shadow p-4 position-sticky" style="top: 1.5rem;">
            <h3 class="h6 fw-bold text-dark mb-3 d-flex align-items-center">
              <span class="me-2">📋</span>
              Booking Summary
            </h3>

            <div class="d-flex flex-column gap-3 small">
              <div class="pb-2 border-bottom">
                <p class="text-muted text-uppercase small mb-1">Doctor</p>
                <p class="fw-semibold mb-0">Dr. {{ doctor.name }}</p>
              </div>

              <div class="pb-2 border-bottom">
                <p class="text-muted text-uppercase small mb-1">Specialization</p>
                <p class="fw-semibold mb-0">{{ doctor.specialization }}</p>
              </div>

              <div v-if="bookingForm.date" class="pb-2 border-bottom">
                <p class="text-muted text-uppercase small mb-1">Date</p>
                <p class="fw-semibold mb-0">{{ formatFullDate(bookingForm.date) }}</p>
              </div>

              <div v-if="bookingForm.time" class="pb-2 border-bottom">
                <p class="text-muted text-uppercase small mb-1">Time</p>
                <p class="fw-semibold mb-0">{{ formatTime(bookingForm.time) }}</p>
              </div>

              <div v-if="bookingForm.reason" class="pb-2">
                <p class="text-muted text-uppercase small mb-1">Reason</p>
                <p class="fw-semibold mb-0">{{ bookingForm.reason }}</p>
              </div>
            </div>

            <div
              v-if="!bookingForm.date"
              class="mt-4 p-3 bg-warning bg-opacity-10 border border-warning border-opacity-50 rounded"
            >
              <p class="small text-warning d-flex mb-0">
                <span class="me-2">💡</span>
                <span>Select a date and time to proceed with booking</span>
              </p>
            </div>

            <div
              v-else-if="!bookingForm.time"
              class="mt-4 p-3 bg-primary bg-opacity-10 border border-primary border-opacity-50 rounded"
            >
              <p class="small text-primary d-flex mb-0">
                <span class="me-2">⏰</span>
                <span>Now select your preferred time slot</span>
              </p>
            </div>

            <div
              v-else
              class="mt-4 p-3 bg-success bg-opacity-10 border border-success border-opacity-50 rounded"
            >
              <p class="small text-success d-flex mb-0">
                <span class="me-2">✓</span>
                <span>Ready to book! Click "Confirm Booking" when ready.</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.bg-gradient-blue {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
</style>
