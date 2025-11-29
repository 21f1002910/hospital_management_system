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
    path: '/admin',
    component: () => import('@components/pages/admin/Layout.vue'),
    meta: { title: `${app_name} - Admin`,
            requiresAuth: true, role: 'Admin'},
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@components/pages/admin/Dashboard.vue'),
      },
      {
        path: 'patients',
        name: 'AdminPatients',
        component: () => import('@components/pages/admin/Patients.vue'),
      },
      {
        path: 'doctors',
        name: 'AdminDoctors',
        component: () => import('@components/pages/admin/Doctors.vue'),
      },
      {
        path: 'appointments',
        name: 'AdminAppointments',
        component: () => import('@components/pages/admin/Appointments.vue'),
      },
      {
        path: 'departments',
        name: 'AdminDepartments',
        component: () => import('@components/pages/admin/Departments.vue'),
      }
    ]
  },
  {
    path: '/doctor',
    component: () => import('@components/pages/doctor/Layout.vue'),
    meta: { title: `${app_name} - Doctor`,
            requiresAuth: true, role: 'Doctor'},
    children: [
      {
        path: 'dashboard',
        name: 'DoctorDashboard',
        component: () => import('@components/pages/doctor/Dashboard.vue'),
      },
      {
        path: 'patients',
        name: 'DoctorPatients',
        component: () => import('@components/pages/doctor/Patients.vue'),
      },
      {
        path: 'patients/:id',
        name: 'DoctorPatientHistory',
        component: () => import('@components/pages/doctor/PatientHistory.vue'),
      },
      {
        path: 'appointments',
        name: 'DoctorAppointments',
        component: () => import('@components/pages/doctor/Appointments.vue'),
      },
      {
        path: 'availability',
        name: 'DoctorAvailability',
        component: () => import('@components/pages/doctor/Availability.vue'),
      }
    ]
  },
  {
    path: '/patient',
    component: () => import('@components/pages/patient/Layout.vue'),
    meta: { title: `${app_name} - Patient`,
            requiresAuth: true, role: 'Patient'},
    children: [
      {
        path: 'dashboard',
        name: 'PatientDashboard',
        component: () => import('@components/pages/patient/Dashboard.vue'),
      },
      {
        path: 'doctors',
        name: 'PatientDoctors',
        component: () => import('@components/pages/patient/Doctors.vue'),
      },
      {
        path: 'doctors/:id',
        name: 'DoctorProfile',
        component: () => import('@components/pages/patient/DoctorProfile.vue'),
      },
      {
        path: 'appointments',
        name: 'PatientAppointments',
        component: () => import('@components/pages/patient/Appointments.vue'),
      },
      {
        path: 'appointments/:id',
        name: 'AppointmentDetails',
        component: () => import('@components/pages/patient/AppointmentDetails.vue'),
      },
      {
        path: 'medical-history',
        name: 'MedicalHistory',
        component: () => import('@components/pages/patient/MedicalHistory.vue'),
      },
      {
        path: 'profile',
        name: 'PatientProfile',
        component: () => import('@components/pages/patient/Profile.vue'),
      }
    ]
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