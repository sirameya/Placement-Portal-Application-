/**
 * router/index.js — maps URLs to views, and protects routes by role.
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  // meta.role: only a logged-in user with THIS role may visit this route
  { path: '/admin', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/company', component: CompanyDashboard, meta: { role: 'company' } },
  { path: '/student', component: StudentDashboard, meta: { role: 'student' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// This function runs BEFORE every single navigation.
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  const requiredRole = to.meta.role
  if (!requiredRole) {
    // Login/Register pages have no role requirement — always allowed
    next()
    return
  }

  if (!auth.isLoggedIn) {
    next('/login')            // not logged in at all -> bounce to login
  } else if (auth.role !== requiredRole) {
    next(`/${auth.role}`)     // logged in, but wrong role -> send to THEIR dashboard
  } else {
    next()                    // correct role -> allow
  }
})

export default router
