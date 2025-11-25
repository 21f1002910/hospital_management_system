<script setup>
import { reactive, ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useStorage } from '@vueuse/core' 
import { useMessageStore } from '../../store/index.js'

const messageStore = useMessageStore()
const router = useRouter()
const form = reactive({ username: '', password: '' })
const loggedIn = ref(false)
const token = useStorage('token', '')
const role = useStorage('role', '')


const handleLogin = async () => {
  messageStore.clear()
  try {
    const response = await axios.post('/api/login', form, {
      validateStatus: status => status < 500
    })
    
    if (response.status === 200) {
      messageStore.showSuccess('Login successful!')
      
      token.value = response.data.access_token
      role.value = response.data.role
      
      if (role.value === 'Admin') {
        router.push({ name: 'AdminHome' })
      } else if (role.value === 'Doctor') {
        router.push({ name: 'DoctorHome' })
      } else if (role.value === 'Patient') {
        router.push({ name: 'PatientHome' })
      }
    } else {
      messageStore.showError(response.data?.message || 'Login failed')
    }
  } catch (error) {
    messageStore.showError(error.message || 'Network error')
    console.error('Login error:', error)
  }
}
</script>

<template>
  <div class="container mt-5">
    <div class="login-box mx-auto p-4 rounded shadow-sm bg-light">
      <h3 class="text-center mb-4">Enter your credentials</h3>
      <form @submit.prevent="handleLogin">
        <div class="form-group row mb-3">
          <label for="username" class="col-sm-4 col-form-label">Username</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" v-model="form.username" placeholder="Enter username" required>
          </div>
        </div>
        <div class="form-group row mb-4">
          <label for="password" class="col-sm-4 col-form-label">Password</label>
          <div class="col-sm-8">
            <input type="password" class="form-control" v-model="form.password" placeholder="Enter password" required>
          </div>
        </div>
        <button type="submit" class="btn btn-success w-50">Login</button>
      </form>

      <div class="text-center">
        <small>
          Don't have an account?
          <router-link :to="{ name:'Register' }">Register here</router-link>
        </small>
      </div>

    </div>
  </div>
</template>


<style scoped>
</style>