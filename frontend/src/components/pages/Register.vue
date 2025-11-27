<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth.js'
import { useMessageStore } from '../../store'

const router = useRouter()
const authStore = useAuthStore()
const messageStore = useMessageStore()

const form = ref({
  name: '',
  email: '',
  contact: '',
  password: '',
  confirm_password: '',
})

const loading = ref(false)

async function handleRegister() {
  // Validation
  if (form.value.password !== form.value.confirm_password) {
    messageStore.error('Passwords do not match')
    return
  }

  if (form.value.password.length < 6) {
    messageStore.error('Password must be at least 6 characters')
    return
  }

  loading.value = true

  try {
    const result = await authStore.register(form.value)

    if (result.success) {
      messageStore.success(result.message)
      router.push('/login')
    } else {
      messageStore.error(result.message || 'Registration failed')
    }
  } catch (error) {
    messageStore.error('An error occurred. Please try again.')
  } finally {
    loading.value = false
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
          <label class="col-sm-4 col-form-label text-start">Full Name</label>
          <div class="col-sm-8">
            <input v-model="form.name" type="text" class="form-control" required>
          </div>
        </div>

        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Email</label>
          <div class="col-sm-8">
            <input v-model="form.email" type="text" class="form-control" required>
          </div>
        </div>

        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Contact Number</label>
          <div class="col-sm-8">
            <input v-model="form.contact" type="tel" class="form-control" required>
          </div>
        </div>

        <div class="form-group row mb-2">
          <label class="col-sm-4 col-form-label text-start">Password</label>
          <div class="col-sm-8">
            <input v-model="form.password" type="password" class="form-control" required>
          </div>
        </div>

        <div class="form-group row mb-3">
          <label class="col-sm-4 col-form-label text-start">Confirm Password</label>
          <div class="col-sm-8">
            <input v-model="form.confirm_password" type="password" class="form-control" required>
          </div>
        </div>

        <button type="submit" class="btn btn-success w-50 mb-2 d-block mx-auto">Register</button>
        <button type="button" class="btn btn-outline-secondary w-50 d-block mx-auto" @click="router.push({ name: 'Login' })">
          Back to Login
        </button>
      </form>
    </div>
  </div>
</template>





<style scoped>
</style>