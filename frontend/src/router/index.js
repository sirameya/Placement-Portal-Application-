import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import DrivesView from '../views/DrivesView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/drives', name: 'drives', component: DrivesView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
