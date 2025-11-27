import { createRouter, createWebHistory } from 'vue-router'
import { app_name} from '../config.js';
import { useAuthStore } from '../store/auth.js'

const routes = [
  {
    path: '/',
    redirect: '/login',
    meta: { title: `${app_name} - Login`,
            requiresGuest: true}
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@components/pages/Login.vue'),
    meta: { title: `${app_name} - Login`,
            requiresGuest: true}
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@components/pages/Register.vue'),
    meta: { title: `${app_name} - Register`,
            requiresGuest: true}
  },
  {
    path: '/admin/dashboard',
    name: 'AdminHome',
    component: () => import('@components/pages/admin/Admin.vue'),
    meta: { title: `${app_name} - Admin Dashboard`,
            requiresAuth: true, role: 'Admin'}
  },
  {
    path: '/patient/dashboard',
    name: 'PatientHome',
    component: () => import('@components/pages/patient/Patient.vue'),
    meta: { title: `${app_name} - Patient Dashboard`,
            requiresAuth: true, role: 'Patient'}
  },
  {
    path: '/doctor/dashboard',
    name: 'DoctorHome',
    component: () => import('@components/pages/doctor/Doctor.vue'),
    meta: { title: `${app_name} - Doctor Dashboard`,
            requiresAuth: true, role: 'Doctor'}
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
  const authStore = useAuthStore()

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }

    // Check role-based access
    if (to.meta.role && authStore.role !== to.meta.role) {
      next(authStore.getDashboardRoute())
      return
    }
  }

  // Redirect authenticated users away from guest pages
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next(authStore.getDashboardRoute())
    return
  }

  next()
})

export default router