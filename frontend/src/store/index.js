import { defineStore } from 'pinia'

export const useMessageStore = defineStore('message', {
  state: () => ({
    message: '',
    type: 'info' // success | error | info
  }),

  actions: {
    showSuccess(msg) {
      this.message = msg
      this.type = 'success'
      this.autoClear()
    },

    showError(msg) {
      this.message = msg
      this.type = 'error'
      this.autoClear()
    },

    showInfo(msg) {
      this.message = msg
      this.type = 'info'
      this.autoClear()
    },

    autoClear() {
      setTimeout(() => {
        this.message = ''
      }, 4000)
    },

    clear() {
      this.message = ''
    }
  }
})
