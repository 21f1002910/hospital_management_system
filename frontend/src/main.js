import { createApp } from 'vue'
import { createPinia } from 'pinia'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap'
import './style.css'

import App from './App.vue'
import router from './router'


const app = createApp(App)
app.use(router)
app.use(createPinia())
app.mount('#app')

router.isReady().then(() => {
  document.title = router.currentRoute.value.meta.title || "HMS"
})