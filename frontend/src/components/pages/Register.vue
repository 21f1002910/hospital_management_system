<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useStorage } from '@vueuse/core' 
import { useMessageStore } from '../../store/index.js'

const router = useRouter()

const username = ref('')
const password = ref('')
const confirm_password = ref('')
const name = ref('')
const age = ref('')
const gender = ref('')
const contact = ref('')
const address = ref('')

const loggedIn = ref(false)
const token = useStorage('token', '')
const role = useStorage('role', '')

async function handleRegister() {
  messageStore.clear()
  if (password.value !== confirm_password.value) {
    messageStore.showError('Passwords do not match')
    return
  }

  try {
    const registerData = {
      username: username.value,
      password: password.value,
      name: name.value,
      age: parseInt(age.value),
      gender: gender.value,
      contact: contact.value,
      address: address.value
    }

    const response = await axios.post('/api/register', registerData, {
      validateStatus: status => status < 500
    })

    if (response.status === 201 || response.status === 200) {
        const loginData = {
        username: username.value,
        password: password.value}
        const loginResponse = await axios.post('/api/login', loginData, {
        validateStatus: status => status < 500
      })
      if (loginResponse.status === 200) {
        token.value = loginResponse.data.access_token
        role.value = loginResponse.data.role
        
        messageStore.showSuccess('Registered successfully! Redirecting to patient dashboard...')

        setTimeout(() => {
          router.push({ name: 'PatientHome' })
        }, 2000)
      } else {
        messageStore.showError('Registration succeeded but login failed. Please login manually.')
        setTimeout(() => {
          router.push({ name: 'Login' })
        }, 2000)
      }
    } else {
      messageStore.showError(response.data?.message || 'Registration failed!')
    }
  } catch (error) {
    messageStore.showError(error.message || 'Network error. Please check backend.')
    console.error('Registration error:', error)
  }
}
</script>

<template>
  <div class="container mt-5">
    <div class="register-box mx-auto p-4 rounded shadow-sm bg-light">

      <div class="text-center mb-3">
        <h3>Patient Registration</h3>
        <small>Create your account to manage your health journey</small>
      </div>

      <form @submit.prevent="handleRegister">
        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Username</label>
          <div class="col-sm-8">
            <input v-model="username" type="text" class="form-control" required>
          </div>
        </div>

        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Full Name</label>
          <div class="col-sm-8">
            <input v-model="name" type="text" class="form-control" required>
          </div>
        </div>

        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Age</label>
          <div class="col-sm-8">
            <input v-model="age" type="number" class="form-control" min="1" max="150" required>
          </div>
        </div>

        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Gender</label>
          <div class="col-sm-8">
            <select v-model="gender" class="form-control" required>
              <option value="">Select</option>
              <option>Male</option>
              <option>Female</option>
              <option>Prefer not to Say</option>
            </select>
          </div>
        </div>

        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Contact Number</label>
          <div class="col-sm-8">
            <input v-model="contact" type="tel" class="form-control">
          </div>
        </div>

        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Address</label>
          <div class="col-sm-8">
            <textarea v-model="address" rows="2" class="form-control"></textarea>
          </div>
        </div>

        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Password</label>
          <div class="col-sm-8">
            <input v-model="password" type="password" class="form-control" required>
          </div>
        </div>

        <div class="form-group row mb-3">
          <label class="col-sm-4 col-form-label text-start">Confirm Password</label>
          <div class="col-sm-8">
            <input v-model="confirm_password" type="password" class="form-control" required>
          </div>
        </div>

        <button type="submit" class="btn btn-success w-50 mb-2 d-block mx-auto">Register</button>
        <button type="button" class="btn btn-outline-secondary w-50 d-block mx-auto" @click="router.push({ name: 'Login' })">
          Back to Login
        </button>

        <div v-if="message" class="alert mt-3 text-center"
            :class="success ? 'alert-success' : 'alert-danger'">
            {{ message }}
        </div>

      </form>
    </div>
  </div>
</template>





<style scoped>
</style>