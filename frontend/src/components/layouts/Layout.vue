<script setup>
import { app_name } from '../../config.js'
import { computed, onMounted} from 'vue'
import { useRouter } from 'vue-router'
import { useStorage } from '@vueuse/core'
import { useMessageStore } from '../../store/index.js'

const messageStore = useMessageStore()
const message = computed(() => messageStore.message)

const router = useRouter()
const token = useStorage('token', '')
const role = useStorage('role', '')
const isLoggedIn = computed(() => !!token.value)


onMounted(() => {
  console.log('Mounted - token:', token.value, 'role:', role.value, 'isLoggedIn:', isLoggedIn.value)
  if (!isLoggedIn.value) {
    router.push({ name: "Login" })
  }
})


function logout() {
  token.value = ''
  role.value = ''
  messageStore.showSuccess('Logged out successfully!')
  router.push({ name: "Login" })
}

function goHome() {
  console.log('goHome clicked - role:', role.value)
  if (role.value === '') {
    router.push({ name: "Login" })
  } else if (role.value === 'Admin') {
    router.push({ name: "AdminHome" })
  } else if (role.value === 'Doctor') {
    router.push({ name: "DoctorHome" })
  } else if (role.value === 'Patient') {
    router.push({ name: "PatientHome" })
  }
}
</script>

<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
        <div class="container-fluid">
            <a href="#" class="navbar-brand" @click.prevent="goHome">
                {{ app_name }}
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNavbar" aria-controls="mainNavbar" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>

        
        <div class="collapse navbar-collapse" id="mainNavbar">
          <ul class="navbar-nav ms-auto" v-if="isLoggedIn">
            <li class="nav-item">
                <button type="button" class="btn btn-outline-danger ms-lg-2" @click="logout">
                    Logout
                </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div v-if="messageStore.message" class="alert text-center" :class="`alert-${messageStore.type}`" style="margin-top: 70px;">
      {{ messageStore.message }}
    </div>

    <main class="app-main">
      <slot />
    </main>

    <footer class="app-footer">
        <small>Created by</small>
    </footer>
  </div>
</template>

<style scoped>
.app-footer {
  margin-top: 40px;
  padding: 20px 0;
  border-top: 1px solid #eee;
  text-align: center;
  color: #777;
  font-size: 13px;
}
</style>
