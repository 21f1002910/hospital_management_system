import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMessageStore = defineStore('message', () => {
  const messages = ref([])

  function addMessage(message, type = 'info') {
    const id = Date.now()
    const newMessage = {
      id,
      text: message,
      type, // 'success', 'error', 'warning', 'info'
      timestamp: new Date()
    }
    
    messages.value.push(newMessage)
    console.log('📢 Message added:', newMessage) // Debug log

    // Auto remove after 5 seconds
    setTimeout(() => {
      removeMessage(id)
    }, 5000)
  }

  function removeMessage(id) {
    messages.value = messages.value.filter(m => m.id !== id)
    console.log('🗑️ Message removed:', id) // Debug log
  }

  function success(message) {
    addMessage(message, 'success')
  }

  function error(message) {
    addMessage(message, 'error')
  }

  function warning(message) {
    addMessage(message, 'warning')
  }

  function info(message) {
    addMessage(message, 'info')
  }

  return {
    messages,
    addMessage,
    removeMessage,
    success,
    error,
    warning,
    info
  }
})