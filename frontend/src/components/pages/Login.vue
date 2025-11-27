<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth.js'
import { useMessageStore } from '../../store'

const router = useRouter()
const authStore = useAuthStore()
const messageStore = useMessageStore()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)

async function handleLogin() {
  loading.value = true

  try {
    const result = await authStore.login(form.value)

    if (result.success) {
      messageStore.success('Login successful!')
      router.push(authStore.getDashboardRoute())
    } else {
      messageStore.error(result.message || 'Invalid credentials')
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
    <div class="login-box mx-auto p-4 rounded shadow-sm bg-light">
      <h3 class="text-center mb-4">Enter your credentials</h3>
      <form @submit.prevent="handleLogin">
        <div class="form-group row mb-3">
          <label for="email" class="col-sm-4 col-form-label">Email</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" v-model="form.email" placeholder="Enter email" required>
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