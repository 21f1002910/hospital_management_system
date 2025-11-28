<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '../../../services/api'
import { useMessageStore } from '../../../store'

const messageStore = useMessageStore()

const doctors = ref([])
const departments = ref([])
const searchQuery = ref('')
const specializationFilter = ref('')
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

const showAddModal = ref(false)
const editingDoctor = ref(null)
const deletingDoctor = ref(null)
const submitting = ref(false)

const form = ref({
  email: '',
  password: '',
  name: '',
  specialization_id: '',
  contact: '',
  bio: ''
})

async function loadDoctors(page = 1) {
  loading.value = true
  try {
    const response = await adminAPI.getDoctors({
      page,
      per_page: 9,
      search: searchQuery.value,
      specialization: specializationFilter.value
    })
    doctors.value = response.data.doctors
    currentPage.value = page
    totalPages.value = response.data.pages
  } catch (error) {
    console.error('Load doctors error:', error)
    messageStore.error('Failed to load doctors')
  } finally {
    loading.value = false
  }
}

async function loadDepartments() {
  try {
    const response = await adminAPI.getDepartments()
    departments.value = response.data.departments
  } catch (error) {
    console.error('Load departments error:', error)
    messageStore.error('Failed to load departments')
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

function editDoctor(doctor) {
  editingDoctor.value = doctor
  form.value = {
    name: doctor.name,
    specialization_id: departments.value.find(d => d.name === doctor.specialization)?.id || '',
    contact: doctor.contact || '',
    bio: doctor.bio || ''
  }
}

function confirmDelete(doctor) {
  deletingDoctor.value = doctor
}

async function saveDoctor() {
  submitting.value = true
  try {
    if (editingDoctor.value) {
      await adminAPI.updateDoctor(editingDoctor.value.id, form.value)
      messageStore.success('Doctor updated successfully')
    } else {
      await adminAPI.createDoctor(form.value)
      messageStore.success('Doctor added successfully')
    }
    closeModal()
    loadDoctors(currentPage.value)
  } catch (error) {
    console.error('Save doctor error:', error)
    messageStore.error(error.response?.data?.message || 'Operation failed')
  } finally {
    submitting.value = false
  }
}

async function deleteDoctor() {
  submitting.value = true
  try {
    await adminAPI.deleteDoctor(deletingDoctor.value.id)
    messageStore.success('Doctor deleted successfully')
    deletingDoctor.value = null
    loadDoctors(currentPage.value)
  } catch (error) {
    console.error('Delete doctor error:', error)
    messageStore.error('Failed to delete doctor')
  } finally {
    submitting.value = false
  }
}

function closeModal() {
  showAddModal.value = false
  editingDoctor.value = null
  form.value = {
    email: '',
    password: '',
    name: '',
    specialization_id: '',
    contact: '',
    bio: ''
  }
}

onMounted(() => {
  loadDoctors()
  loadDepartments()
})
</script>

<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0">Doctors Management</h1>
      <button @click="showAddModal = true" class="btn btn-success">+ Add Doctor</button>
    </div>

    <!-- Search and Filter -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row gx-3 gy-2">
          <div class="col-12 col-md-4">
            <input
              v-model="searchQuery"
              @keyup.enter="searchDoctors"
              type="text"
              placeholder="Search by name or email..."
              class="form-control"
            />
          </div>

          <div class="col-12 col-md-4">
            <select v-model="specializationFilter" @change="searchDoctors" class="form-select">
              <option value="">All Specializations</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                {{ dept.name }}
              </option>
            </select>
          </div>

          <div class="col-12 col-md-4 d-flex gap-2">
            <button @click="searchDoctors" class="btn btn-primary flex-fill">Search</button>
            <button @click="clearFilters" class="btn btn-secondary flex-fill">Clear</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="doctors.length === 0" class="card text-center p-4 text-muted">
      No doctors found
    </div>

    <!-- Grid -->
    <div v-else class="row g-3">
      <div v-for="doctor in doctors" :key="doctor.id" class="col-12 col-md-6 col-lg-4">
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between mb-2">
              <div>
                <h5 class="card-title mb-1">{{ doctor.name }}</h5>
                <p class="mb-1 small text-primary">{{ doctor.specialization }}</p>
                <p class="mb-0 small text-muted">{{ doctor.email }}</p>
              </div>
            </div>

            <p v-if="doctor.bio" class="text-muted small mb-2">{{ doctor.bio }}</p>

            <p v-if="doctor.contact" class="text-muted small mb-3">📞 {{ doctor.contact }}</p>

            <div class="mt-auto d-flex gap-2">
              <button @click="editDoctor(doctor)" class="btn btn-primary btn-sm flex-fill">Edit</button>
              <button @click="confirmDelete(doctor)" class="btn btn-danger btn-sm flex-fill">Delete</button>
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
        @click="loadDoctors(page)"
        :class="['btn btn-sm', currentPage === page ? 'btn-primary' : 'btn-outline-secondary']"
      >
        {{ page }}
      </button>
    </div>

    <!-- Add/Edit Doctor Modal (v-if + backdrop) -->
    <div
      v-if="showAddModal || editingDoctor"
      class="modal d-block"
      tabindex="-1"
      @click.self="closeModal"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingDoctor ? 'Edit Doctor' : 'Add New Doctor' }}</h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>

          <form @submit.prevent="saveDoctor">
            <div class="modal-body">
              <div v-if="!editingDoctor" class="mb-3">
                <label class="form-label">Email *</label>
                <input
                  v-model="form.email"
                  type="email"
                  required
                  class="form-control"
                  placeholder="doctor@example.com"
                />
              </div>

              <div v-if="!editingDoctor" class="mb-3">
                <label class="form-label">Password *</label>
                <input
                  v-model="form.password"
                  type="password"
                  required
                  minlength="6"
                  class="form-control"
                  placeholder="Minimum 6 characters"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Full Name *</label>
                <input v-model="form.name" type="text" required class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">Specialization *</label>
                <select v-model="form.specialization_id" required class="form-select">
                  <option value="">Select Department</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Contact</label>
                <input v-model="form.contact" type="tel" class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">Bio</label>
                <textarea v-model="form.bio" rows="3" class="form-control"></textarea>
              </div>
            </div>

            <div class="modal-footer">
              <button type="submit" :disabled="submitting" class="btn btn-success">
                {{ submitting ? 'Saving...' : 'Save' }}
              </button>
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deletingDoctor"
      class="modal d-block"
      tabindex="-1"
      @click.self="deletingDoctor = null"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="deletingDoctor = null" aria-label="Close"></button>
          </div>

          <div class="modal-body">
            <p class="mb-3">
              Are you sure you want to delete Dr. <strong>{{ deletingDoctor.name }}</strong>? This action cannot be undone.
            </p>
          </div>

          <div class="modal-footer">
            <button @click="deleteDoctor" :disabled="submitting" class="btn btn-danger">
              {{ submitting ? 'Deleting...' : 'Delete' }}
            </button>
            <button @click="deletingDoctor = null" class="btn btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
