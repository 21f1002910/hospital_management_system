<script setup>
import { useMessageStore } from '../../store'

const messageStore = useMessageStore()
</script>

<template>
    <div class="position-fixed top-0 start-50 translate-middle-x p-3" style="z-index: 9999;">
        <div
            v-for="message in messageStore.messages"
            :key="message.id"
            class="toast show mb-2"
            role="alert"
            @click="messageStore.removeMessage(message.id)"
            style="min-width: 300px; cursor: pointer;"
        >
            <div 
                class="toast-header text-white"
                :class="{
                    'bg-success': message.type === 'success',
                    'bg-danger': message.type === 'error',
                    'bg-warning': message.type === 'warning',
                    'bg-info': message.type === 'info'
                }"
            >
                <strong class="me-auto">
                    <span v-if="message.type === 'success'">✓ Success</span>
                    <span v-if="message.type === 'error'">✕ Error</span>
                    <span v-if="message.type === 'warning'">⚠ Warning</span>
                    <span v-if="message.type === 'info'">ℹ Info</span>
                </strong>
                <button 
                    type="button" 
                    class="btn-close btn-close-white" 
                    @click.stop="messageStore.removeMessage(message.id)"
                ></button>
            </div>
            <div class="toast-body">
                {{ message.text }}
            </div>
        </div>
    </div>
</template>

<style scoped>
</style>