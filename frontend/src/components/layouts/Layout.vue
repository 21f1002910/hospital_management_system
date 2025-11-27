<script setup>
import { app_name } from '../../config.js'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth.js'
import { useMessageStore } from '../../store'
import Toast from './Toast.vue'


const router = useRouter()
const authStore = useAuthStore()
const messageStore = useMessageStore()

function handleLogout() {
  authStore.logout()
  messageStore.info('Logged out successfully')
  router.push('/login')
}
</script>

<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
        <div class="container-fluid">
            <a href="#" class="navbar-brand" @click="router.push(authStore.getDashboardRoute())">
                {{ app_name }}
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNavbar" aria-controls="mainNavbar" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
        
        <div class="collapse navbar-collapse" id="mainNavbar">
          <ul class="navbar-nav ms-auto" v-if="authStore.isAuthenticated">
            <li class="nav-item">
                <button type="button" class="btn btn-outline-danger ms-lg-2" @click="handleLogout">
                    Logout
                </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <Toast />
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
