import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useStorage } from '@vueuse/core'
import { authAPI } from '../services/api.js'

export const useAuthStore = defineStore('auth', () => {
  // State - persisted in localStorage
  const token = useStorage('token', null)
  const role = useStorage('role', null)
  const email = useStorage('email', null)  // Changed from username to email

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'Admin')
  const isDoctor = computed(() => role.value === 'Doctor')
  const isPatient = computed(() => role.value === 'Patient')

  // Actions
  async function login(credentials) {
    try {
      const response = await authAPI.login(credentials)
      
      if (response.status === 200) {
        token.value = response.data.access_token
        role.value = response.data.role
        email.value = credentials.email  // Store email instead of username
        return { success: true, role: response.data.role }
      } else {
        return { success: false, message: response.data.message }
      }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, message: 'Login failed. Please try again.' }
    }
  }

  async function register(userData) {
    try {
      const response = await authAPI.register(userData)
      
      if (response.status === 201) {
        await login({
        email: userData.email,
        password: userData.password
      })
        return { success: true, message: 'Registration successful!' }
      } else {
        return { success: false, message: response.data.message }
      }
    } catch (error) {
      console.error('Registration error:', error)
      return { success: false, message: 'Registration failed. Please try again.' }
    }
  }

  function logout() {
    token.value = null
    role.value = null
    email.value = null
  }

  function getDashboardRoute() {
    if (isAdmin.value) return '/admin/dashboard'
    if (isDoctor.value) return '/doctor/dashboard'
    if (isPatient.value) return '/patient/dashboard'
    return '/login'
  }

  return {
    // State
    token,
    role,
    email,  // Changed from username
    // Getters
    isAuthenticated,
    isAdmin,
    isDoctor,
    isPatient,
    // Actions
    login,
    register,
    logout,
    getDashboardRoute
  }
})