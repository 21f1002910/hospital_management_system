<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { doctorAPI } from '../../../services/api.js'
import { useMessageStore } from '../../../store'

const route = useRoute()
const messageStore = useMessageStore()

const patientData = ref(null)
const loading = ref(false)

async function loadPatientHistory() {
  loading.value = true
  try {
    const response = await doctorAPI.getPatientDetails(route.params.id)
    patientData.value = response.data
  } catch (error) {
    console.error('Load patient history error:', error)
    messageStore.error('Failed to load patient history')
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(() => {
  loadPatientHistory()
})
</script>


<template>
  <div class="container my-4">
    <button @click="$router.back()" class="btn btn-link mb-4">← Back to Patients</button>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>
      <span class="visually-hidden">Loading...</span>
    </div>

    <!-- Patient details -->
    <div v-else-if="patientData">
      <!-- Patient Info Card -->
      <div class="card mb-4">
        <div class="card-body">
          <h1 class="h4 fw-bold mb-3">{{ patientData.patient.name }}</h1>

          <div class="row g-3">
            <div class="col-6 col-md-3">
              <div class="small text-muted">Age</div>
              <div class="fw-medium">{{ patientData.patient.age }} years</div>
            </div>

            <div class="col-6 col-md-3">
              <div class="small text-muted">Gender</div>
              <div class="fw-medium">{{ patientData.patient.gender }}</div>
            </div>

            <div class="col-6 col-md-3">
              <div class="small text-muted">Blood Group</div>
              <div class="fw-medium">{{ patientData.patient.blood_group || 'N/A' }}</div>
            </div>

            <div class="col-6 col-md-3">
              <div class="small text-muted">Contact</div>
              <div class="fw-medium">{{ patientData.patient.contact }}</div>
            </div>
          </div>

          <div v-if="patientData.patient.allergies" class="mt-3 alert alert-danger">
            <strong>⚠️ Allergies:</strong>
            <div class="mt-2">{{ patientData.patient.allergies }}</div>
          </div>
        </div>
      </div>

      <!-- Medical History -->
      <h2 class="h5 fw-bold mb-3">Medical History</h2>

      <div v-if="patientData.medical_history.length === 0" class="card text-center p-4 text-muted mb-3">
        No medical history available
      </div>

      <div v-else class="mb-3">
        <div v-for="record in patientData.medical_history" :key="record.id" class="card mb-3">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <div>
                <h6 class="mb-1">{{ formatDate(record.date) }} at {{ record.time }}</h6>
                <div class="small text-muted">{{ record.reason || 'General consultation' }}</div>
              </div>

              <span
                class="badge"
                :class="record.status === 'Completed' ? 'bg-success' : record.status === 'Booked' ? 'bg-primary' : 'bg-secondary'"
              >
                {{ record.status }}
              </span>
            </div>

            <div v-if="record.treatment" class="border-top pt-3">
              <div class="mb-2">
                <div class="small text-muted">Diagnosis</div>
                <div class="fw-medium">{{ record.treatment.diagnosis }}</div>
              </div>

              <div v-if="record.treatment.prescription" class="mb-2">
                <div class="small text-muted">Prescription</div>
                <pre class="mb-0">{{ record.treatment.prescription }}</pre>
              </div>

              <div v-if="record.treatment.notes">
                <div class="small text-muted">Notes</div>
                <div>{{ record.treatment.notes }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
