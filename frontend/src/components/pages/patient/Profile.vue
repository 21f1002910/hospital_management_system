<script setup>
import { ref, onMounted } from 'vue'
import { patientAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'


const messageStore = useMessageStore()

const form = ref({
  name: '',
  email: '',
  age: null,
  gender: '',
  contact: '',
  address: '',
  blood_group: '',
  allergies: ''
})

const originalForm = ref({})
const loading = ref(false)
const editing = ref(false)
const submitting = ref(false)

async function loadProfile() {
  loading.value = true
  try {
    const response = await patientAPI.getProfile()
    form.value = { ...response.data }
    originalForm.value = { ...response.data }
  } catch (error) {
    console.error('Load profile error:', error)
    messageStore.error('Failed to load profile')
  } finally {
    loading.value = false
  }
}

async function updateProfile() {
  submitting.value = true
  try {
    await patientAPI.updateProfile(form.value)
    messageStore.success('Profile updated successfully!')
    originalForm.value = { ...form.value }
    editing.value = false
  } catch (error) {
    console.error('Update profile error:', error)
    messageStore.error(error.response?.data?.message || 'Failed to update profile')
  } finally {
    submitting.value = false
  }
}

function cancelEdit() {
  form.value = { ...originalForm.value }
  editing.value = false
}

function getInitials(name) {
  if (!name) return '??'
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

onMounted(() => {
  loadProfile()
})
</script>


<template>
  <div class="container my-4">
    <h1 class="display-6 fw-bold mb-4">My Profile</h1>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border" role="status" style="width: 3rem; height: 3rem;">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="mx-auto" style="max-width: 900px;">
      <!-- Profile Header -->
      <div class="card text-white mb-4" style="background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);">
        <div class="card-body">
          <div class="d-flex align-items-center">
            <div
              class="rounded-circle d-flex align-items-center justify-content-center bg-white bg-opacity-25 me-3"
              :style="{ width: '96px', height: '96px', fontSize: '1.75rem', fontWeight: 700 }"
            >
              {{ getInitials(form.name) }}
            </div>

            <div>
              <h2 class="h4 mb-1 fw-bold">{{ form.name }}</h2>
              <p class="mb-0 text-white-50">{{ form.email }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Form -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h3 class="h6 fw-bold mb-0">Personal Information</h3>
            <button
              v-if="!editing"
              @click="editing = true"
              type="button"
              class="btn btn-primary"
            >
              Edit Profile
            </button>
          </div>

          <form @submit.prevent="updateProfile" class="row g-3">
            <!-- Name -->
            <div class="col-12 col-md-6">
              <label class="form-label">
                Full Name <span class="text-danger">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                required
                :disabled="!editing"
                class="form-control"
              />
            </div>

            <!-- Email (Read-only) -->
            <div class="col-12 col-md-6">
              <label class="form-label">Email</label>
              <input
                v-model="form.email"
                type="email"
                disabled
                class="form-control"
              />
              <div class="form-text">Email cannot be changed</div>
            </div>

            <!-- Age -->
            <div class="col-12 col-md-6">
              <label class="form-label">Age</label>
              <input
                v-model.number="form.age"
                type="number"
                min="1"
                max="120"
                :disabled="!editing"
                class="form-control"
              />
            </div>

            <!-- Gender -->
            <div class="col-12 col-md-6">
              <label class="form-label">Gender</label>
              <select
                v-model="form.gender"
                :disabled="!editing"
                class="form-select"
              >
                <option value="">Select gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <!-- Contact -->
            <div class="col-12 col-md-6">
              <label class="form-label">
                Contact Number <span class="text-danger">*</span>
              </label>
              <input
                v-model="form.contact"
                type="tel"
                required
                :disabled="!editing"
                class="form-control"
              />
            </div>

            <!-- Blood Group -->
            <div class="col-12 col-md-6">
              <label class="form-label">Blood Group</label>
              <select
                v-model="form.blood_group"
                :disabled="!editing"
                class="form-select"
              >
                <option value="">Select blood group</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
              </select>
            </div>

            <!-- Address -->
            <div class="col-12">
              <label class="form-label">Address</label>
              <textarea
                v-model="form.address"
                rows="3"
                :disabled="!editing"
                class="form-control"
                placeholder="Enter your full address..."
              ></textarea>
            </div>

            <!-- Allergies -->
            <div class="col-12">
              <label class="form-label">
                Allergies <small class="text-muted">(Important for doctors)</small>
              </label>
              <textarea
                v-model="form.allergies"
                rows="3"
                :disabled="!editing"
                class="form-control"
                placeholder="List any allergies (medications, food, etc.)..."
              ></textarea>
              <div class="form-text">
                ⚠️ This information will be shown to doctors during appointments
              </div>
            </div>

            <!-- Action Buttons -->
            <div v-if="editing" class="col-12 d-flex gap-2 border-top pt-3">
              <button
                type="submit"
                :disabled="submitting"
                class="btn btn-success flex-grow-1"
              >
                {{ submitting ? 'Saving...' : 'Save Changes' }}
              </button>
              <button
                type="button"
                @click="cancelEdit"
                class="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Additional Info -->
      <div class="row row-cols-1 row-cols-md-2 g-3">
        <div class="col">
          <div class="card h-100">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title fw-semibold mb-3">
                <span class="me-2">🔒</span> Account Security
              </h5>
              <p class="card-text text-muted mb-3">
                Keep your account secure by using a strong password
              </p>
              <button class="btn btn-outline-dark mt-auto w-100">Change Password</button>
            </div>
          </div>
        </div>

        <div class="col">
          <div class="card h-100">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title fw-semibold mb-3">
                <span class="me-2">📋</span> Medical Records
              </h5>
              <p class="card-text text-muted mb-3">
                View your complete medical history and past appointments
              </p>
              <router-link
                to="/patient/medical-history"
                class="btn btn-primary mt-auto w-100 text-center"
              >
                View History
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
