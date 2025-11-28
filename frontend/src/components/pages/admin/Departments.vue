<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '../../../services/api'
import { useMessageStore } from '../../../store'

const messageStore = useMessageStore()

const departments = ref([])
const loading = ref(false)
const submitting = ref(false)

const showAddModal = ref(false)
const editingDept = ref(null)
const deletingDept = ref(null)

const form = ref({
  name: '',
  description: ''
})

async function loadDepartments() {
  loading.value = true
  try {
    const response = await adminAPI.getDepartments()
    departments.value = response.data.departments
  } catch (error) {
    messageStore.error('Failed to load departments')
  } finally {
    loading.value = false
  }
}

function editDepartment(dept) {
  editingDept.value = dept
  form.value = {
    name: dept.name,
    description: dept.description || ''
  }
}

function confirmDelete(dept) {
  if (dept.doctor_count > 0) {
    messageStore.warning('Cannot delete department with assigned doctors')
    return
  }
  deletingDept.value = dept
}

async function saveDepartment() {
  submitting.value = true
  try {
    if (editingDept.value) {
      await adminAPI.updateDepartment(editingDept.value.id, form.value)
      messageStore.success('Department updated successfully')
    } else {
      await adminAPI.createDepartment(form.value)
      messageStore.success('Department added successfully')
    }
    closeModal()
    loadDepartments()
  } catch (error) {
    messageStore.error(error.response?.data?.message || 'Operation failed')
  } finally {
    submitting.value = false
  }
}

async function deleteDepartment() {
  submitting.value = true
  try {
    await adminAPI.deleteDepartment(deletingDept.value.id)
    messageStore.success('Department deleted successfully')
    deletingDept.value = null
    loadDepartments()
  } catch (error) {
    messageStore.error(error.response?.data?.message || 'Failed to delete department')
  } finally {
    submitting.value = false
  }
}

function closeModal() {
  showAddModal.value = false
  editingDept.value = null
  form.value = {
    name: '',
    description: ''
  }
}

onMounted(() => {
  loadDepartments()
})
</script>

<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0">Departments</h1>
      <button @click="showAddModal = true" class="btn btn-success">
        + Add Department
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="departments.length === 0" class="bg-light rounded p-5 text-center text-muted">
      No departments found
    </div>

    <!-- Grid -->
    <div v-else class="row g-3">
      <div v-for="dept in departments" :key="dept.id" class="col-12 col-md-6 col-lg-4">
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between mb-3">
              <div>
                <h5 class="card-title mb-1">{{ dept.name }}</h5>
                <p class="card-text mb-1 text-muted">{{ dept.description || 'No description' }}</p>
                <p class="mb-0 small text-primary">
                  {{ dept.doctor_count }} {{ dept.doctor_count === 1 ? 'Doctor' : 'Doctors' }}
                </p>
              </div>
            </div>

            <div class="mt-auto d-flex gap-2">
              <button @click="editDepartment(dept)" class="btn btn-primary btn-sm flex-fill">
                Edit
              </button>

              <button
                @click="confirmDelete(dept)"
                :disabled="dept.doctor_count > 0"
                :title="dept.doctor_count > 0 ? 'Cannot delete department with assigned doctors' : ''"
                class="btn btn-danger btn-sm flex-fill"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal (simple Bootstrap modal markup, shown with v-if) -->
    <div
      v-if="showAddModal || editingDept"
      class="modal d-block"
      tabindex="-1"
      role="dialog"
      @click.self="closeModal"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-md modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingDept ? 'Edit Department' : 'Add New Department' }}
            </h5>
            <button type="button" class="btn-close" aria-label="Close" @click="closeModal"></button>
          </div>

          <form @submit.prevent="saveDepartment">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Department Name *</label>
                <input
                  v-model="form.name"
                  type="text"
                  required
                  placeholder="e.g., Cardiology, Neurology"
                  class="form-control"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea
                  v-model="form.description"
                  rows="3"
                  placeholder="Brief description of the department..."
                  class="form-control"
                ></textarea>
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
      v-if="deletingDept"
      class="modal d-block"
      tabindex="-1"
      role="dialog"
      @click.self="deletingDept = null"
      style="background: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog modal-md modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" aria-label="Close" @click="deletingDept = null"></button>
          </div>
          <div class="modal-body">
            <p>
              Are you sure you want to delete the <strong>{{ deletingDept.name }}</strong> department?
              This action cannot be undone.
            </p>
          </div>
          <div class="modal-footer">
            <button @click="deleteDepartment" :disabled="submitting" class="btn btn-danger">
              {{ submitting ? 'Deleting...' : 'Delete' }}
            </button>
            <button @click="deletingDept = null" class="btn btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
