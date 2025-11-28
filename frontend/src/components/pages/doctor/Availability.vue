<script setup>
import { ref, computed, onMounted } from 'vue'
import { doctorAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const messageStore = useMessageStore()

const availabilities = ref([])
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const editingAvailability = ref(null)
const deletingAvailability = ref(null)

const form = ref({
  date: '',
  time_slots: ['09:00']
})

const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const maxDate = computed(() => {
  const date = new Date()
  date.setDate(date.getDate() + 7)
  return date.toISOString().split('T')[0]
})

const sortedAvailabilities = computed(() => {
  return [...availabilities.value].sort((a, b) => new Date(a.date) - new Date(b.date))
})

async function loadAvailability() {
  loading.value = true
  try {
    const response = await doctorAPI.getAvailability()
    availabilities.value = response.data.availabilities
  } catch (error) {
    console.error('Load availability error:', error)
    messageStore.error('Failed to load availability')
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  showModal.value = true
  editingAvailability.value = null
  form.value = {
    date: today.value,
    time_slots: ['09:00']
  }
}

function addTimeSlot() {
  form.value.time_slots.push('')
}

function removeTimeSlot(index) {
  if (form.value.time_slots.length > 1) {
    form.value.time_slots.splice(index, 1)
  }
}

function editAvailability(av) {
  editingAvailability.value = av
  showModal.value = true
  form.value = {
    date: av.date,
    time_slots: [...av.time_slots].sort()
  }
}

function confirmDelete(av) {
  deletingAvailability.value = av
}

async function saveAvailability() {
  // Validate time slots
  const uniqueSlots = [...new Set(form.value.time_slots.filter(s => s))]
  if (uniqueSlots.length === 0) {
    messageStore.error('Please add at least one time slot')
    return
  }

  submitting.value = true
  try {
    if (editingAvailability.value) {
      await doctorAPI.updateAvailability(editingAvailability.value.id, {
        time_slots: uniqueSlots.sort()
      })
      messageStore.success('Availability updated successfully')
    } else {
      await doctorAPI.addAvailability({
        date: form.value.date,
        time_slots: uniqueSlots.sort()
      })
      messageStore.success('Availability added successfully')
    }
    closeModal()
    loadAvailability()
  } catch (error) {
    console.error('Save availability error:', error)
    messageStore.error(error.response?.data?.message || 'Failed to save availability')
  } finally {
    submitting.value = false
  }
}

async function deleteAvailability() {
  submitting.value = true
  try {
    await doctorAPI.deleteAvailability(deletingAvailability.value.id)
    messageStore.success('Availability deleted successfully')
    deletingAvailability.value = null
    loadAvailability()
  } catch (error) {
    console.error('Delete availability error:', error)
    messageStore.error('Failed to delete availability')
  } finally {
    submitting.value = false
  }
}

function closeModal() {
  showModal.value = false
  editingAvailability.value = null
  form.value = {
    date: '',
    time_slots: ['09:00']
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

function getDayOfWeek(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase()
}

function getDay(dateStr) {
  const date = new Date(dateStr)
  return date.getDate()
}

function getMonthYear(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

function formatTime(time) {
  const [hours, minutes] = time.split(':')
  const hour = parseInt(hours)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const displayHour = hour % 12 || 12
  return `${displayHour}:${minutes} ${ampm}`
}

onMounted(() => {
  loadAvailability()
})
</script>

<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <h1 class="h3 fw-bold">Manage Availability</h1>
        <p class="text-muted mb-0">Set your available time slots for the next 7 days</p>
      </div>

      <button @click="openAddModal" class="btn btn-success">
        + Add Availability
      </button>
    </div>

    <!-- Info Card -->
    <div class="alert alert-info d-flex align-items-start">
      <div class="me-3 fs-3">💡</div>
      <div>
        <div class="fw-semibold text-primary mb-1">How it works</div>
        <div class="small">
          Set your available time slots for specific dates. Patients can only book appointments during these slots.
          You can update or remove availability anytime.
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>

    <!-- Empty state -->
    <div v-else-if="availabilities.length === 0" class="card text-center p-4">
      <div class="display-1 mb-3">📅</div>
      <h5 class="fw-semibold mb-2">No availability set</h5>
      <p class="text-muted mb-3">Click "Add Availability" to set your available time slots</p>
      <button @click="openAddModal" class="btn btn-primary">Get Started</button>
    </div>

    <!-- Calendar / Availabilities -->
    <div v-else class="row g-3">
      <div v-for="av in sortedAvailabilities" :key="av.id" class="col-12 col-md-6 col-lg-4 col-xl-3">
        <div class="card h-100">
          <!-- Date Header -->
          <div class="card-header text-white" style="background: linear-gradient(90deg,#0d6efd,#0b5ed7);">
            <div class="small mb-1">{{ getDayOfWeek(av.date) }}</div>
            <div class="h4 fw-bold mb-0">{{ getDay(av.date) }}</div>
            <div class="small opacity-75">{{ getMonthYear(av.date) }}</div>
          </div>

          <!-- Time Slots -->
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div class="fw-semibold">Available Slots</div>
              <div class="small text-muted">({{ av.time_slots.length }})</div>
            </div>

            <div class="mb-3">
              <div v-for="(slot, index) in av.time_slots" :key="index" class="d-flex align-items-center mb-2">
                <div class="badge bg-light text-primary me-2">🕐</div>
                <div class="small">{{ formatTime(slot) }}</div>
              </div>
            </div>

            <div class="d-flex gap-2">
              <button @click="editAvailability(av)" class="btn btn-primary btn-sm flex-grow-1">Edit</button>
              <button @click="confirmDelete(av)" class="btn btn-outline-danger btn-sm">🗑️</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal (v-if + backdrop) -->
    <div
      v-if="showModal"
      class="modal d-block"
      tabindex="-1"
      @click.self="closeModal"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingAvailability ? 'Edit' : 'Add' }} Availability</h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>

          <form @submit.prevent="saveAvailability">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Date <span class="text-danger">*</span></label>
                <input
                  v-model="form.date"
                  type="date"
                  required
                  :min="today"
                  :max="maxDate"
                  :disabled="!!editingAvailability"
                  class="form-control"
                />
                <div class="form-text">You can only set availability for the next 7 days</div>
              </div>

              <div class="mb-3">
                <label class="form-label">Time Slots <span class="text-danger">*</span></label>

                <div v-for="(slot, index) in form.time_slots" :key="index" class="input-group mb-2">
                  <input
                    v-model="form.time_slots[index]"
                    type="time"
                    required
                    class="form-control"
                  />
                  <button
                    v-if="form.time_slots.length > 1"
                    type="button"
                    @click="removeTimeSlot(index)"
                    class="btn btn-outline-danger"
                    title="Remove slot"
                  >
                    ✕
                  </button>
                </div>

                <button type="button" @click="addTimeSlot" class="btn btn-sm btn-outline-secondary w-100">
                  + Add Another Time Slot
                </button>

                <div class="form-text mt-2">Example: 09:00, 10:00, 14:00</div>
              </div>
            </div>

            <div class="modal-footer">
              <button type="submit" :disabled="submitting" class="btn btn-success">
                {{ submitting ? (editingAvailability ? 'Saving...' : 'Saving...') : 'Save Availability' }}
              </button>
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deletingAvailability"
      class="modal d-block"
      tabindex="-1"
      @click.self="deletingAvailability = null"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="deletingAvailability = null" aria-label="Close"></button>
          </div>

          <div class="modal-body">
            <p>
              Are you sure you want to delete availability for
              <strong>{{ formatDate(deletingAvailability.date) }}</strong>?
              This will remove all {{ deletingAvailability.time_slots.length }} time slots.
            </p>
          </div>

          <div class="modal-footer">
            <button @click="deleteAvailability" :disabled="submitting" class="btn btn-danger">
              {{ submitting ? 'Deleting...' : 'Yes, Delete' }}
            </button>
            <button @click="deletingAvailability = null" class="btn btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
