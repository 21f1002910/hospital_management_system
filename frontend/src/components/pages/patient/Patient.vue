<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../../store/auth.js'
import { useMessageStore } from '../../../store'


const router = useRouter()
const authStore = useAuthStore()
const messageStore = useMessageStore()

</script>

<template>
    <div>Welcome {{authStore.email}}!</div>
</template>

<style scoped>
</style>