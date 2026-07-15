/**
 * main.js — the very first JS file that runs. It:
 *   1. Creates the Vue app from App.vue
 *   2. Plugs in Pinia (so any component can use our stores)
 *   3. Plugs in the router (so URL changes swap views)
 *   4. Mounts everything into <div id="app"> from index.html
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './styles.css'

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  })
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
