// Centralized API service with Axios
import axios from 'axios'
import { useAuthStore } from '../store/auth.js'

// Base API configuration
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - Add token to all requests
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ============= AUTH ENDPOINTS =============
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data)
}

// ============= ADMIN ENDPOINTS (ADD TO YOUR EXISTING api.js) =============
export const adminAPI = {
  // Dashboard
  getDashboard: () => api.get('/admin/dashboard'),
  
  // Patients
  getPatients: (params) => api.get('/admin/patients', { params }),
  getPatient: (id) => api.get(`/admin/patients/${id}`),
  searchPatients: (search, page = 1) => api.get('/admin/patients', {
    params: { search, page, per_page: 10 }
  }),
  
  // Doctors
  getDoctors: (params) => api.get('/admin/doctors', { params }),
  getDoctor: (id) => api.get(`/admin/doctors/${id}`),
  createDoctor: (data) => api.post('/admin/doctors', data),
  updateDoctor: (id, data) => api.put(`/admin/doctors/${id}`, data),
  deleteDoctor: (id) => api.delete(`/admin/doctors/${id}`),
  searchDoctors: (search, specialization = '', page = 1) => api.get('/admin/doctors', {
    params: { search, specialization, page, per_page: 10 }
  }),
  
  // Appointments
  getAppointments: (params) => api.get('/admin/appointments', { params }),
  getAppointment: (id) => api.get(`/admin/appointments/${id}`),
  updateAppointment: (id, data) => api.put(`/admin/appointments/${id}`, data),
  filterAppointments: (filters) => api.get('/admin/appointments', { params: filters }),
  
  // Departments
  getDepartments: () => api.get('/admin/departments'),
  createDepartment: (data) => api.post('/admin/departments', data),
  updateDepartment: (id, data) => api.put(`/admin/departments/${id}`, data),
  deleteDepartment: (id) => api.delete(`/admin/departments/${id}`)
}


// ============= DOCTOR ENDPOINTS (ADD TO YOUR EXISTING api.js) =============
export const doctorAPI = {
  // Dashboard
  getDashboard: () => api.get('/doctor/dashboard'),
  
  // Profile
  getProfile: () => api.get('/doctor/profile'),
  updateProfile: (data) => api.put('/doctor/profile', data),
  
  // Appointments
  getAppointments: (params) => api.get('/doctor/appointments', { params }),
  getAppointment: (id) => api.get(`/doctor/appointments/${id}`),
  updateAppointment: (id, data) => api.put(`/doctor/appointments/${id}`, data),
  
  // Treatments
  addTreatment: (appointmentId, data) => api.post(`/doctor/appointments/${appointmentId}/treatment`, data),
  updateTreatment: (treatmentId, data) => api.put(`/doctor/treatments/${treatmentId}`, data),
  
  // Patients
  getPatients: () => api.get('/doctor/patients'),
  getPatientDetails: (id) => api.get(`/doctor/patients/${id}`),
  
  // Availability
  getAvailability: () => api.get('/doctor/availability'),
  addAvailability: (data) => api.post('/doctor/availability', data),
  updateAvailability: (id, data) => api.put(`/doctor/availability/${id}`, data),
  deleteAvailability: (id) => api.delete(`/doctor/availability/${id}`)
}

// ============= PATIENT ENDPOINTS (ADD TO YOUR EXISTING api.js) =============
export const patientAPI = {
  // Dashboard
  getDashboard: () => api.get('/patient/dashboard'),
  
  // Profile
  getProfile: () => api.get('/patient/profile'),
  updateProfile: (data) => api.put('/patient/profile', data),
  
  // Doctors
  getDoctors: (params) => api.get('/patient/doctors', { params }),
  getDoctor: (id) => api.get(`/patient/doctors/${id}`),
  getDepartments: () => api.get('/patient/departments'),
  searchDoctors: (search, specialization = '', page = 1) => api.get('/patient/doctors', {
    params: { search, specialization, page, per_page: 12 }
  }),
  
  // Appointments
  getAppointments: (params) => api.get('/patient/appointments', { params }),
  getAppointment: (id) => api.get(`/patient/appointments/${id}`),
  bookAppointment: (data) => api.post('/patient/appointments', data),
  rescheduleAppointment: (id, data) => api.put(`/patient/appointments/${id}`, data),
  cancelAppointment: (id) => api.delete(`/patient/appointments/${id}`),
  
  // Medical History
  getMedicalHistory: () => api.get('/patient/medical-history')
}


export default api