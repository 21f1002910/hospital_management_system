import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/pages/Login.vue'
import Register from '../components/pages/Register.vue'
import AdminHome from '../components/pages/admin/Admin.vue'
import DoctorHome from '../components/pages/admin/Doctor.vue'
import PatientHome from '../components/pages/admin/Patient.vue'
import { app_name} from '../config.js';

const routes = [
  {
    path: '/',
    redirect: '/login',
    meta: { title: `${app_name} - Login` }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: `${app_name} - Login` }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: `${app_name} - Register` }
  },
  {
    path: '/admin',
    name: 'AdminHome',
    component: AdminHome,
    meta: { title: `${app_name} - Admin Dashboard`,
            requiresAuth: true }
  },
  {
    path: '/doctor',
    name: 'DoctorHome',
    component: DoctorHome,
    meta: { title: `${app_name} - Doctor Dashboard`,
            requiresAuth: true }
  },
  {
    path: '/patient',
    name: 'PatientHome',
    component: PatientHome,
    meta: { title: `${app_name} - Patient Dashboard`,
            requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: routes
})

router.afterEach((to) => {
  document.title = to.meta.title || app_name
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = !!localStorage.getItem('token')

  if (to.matched.some(record => record.meta.requiresAuth) && !isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})


export default router