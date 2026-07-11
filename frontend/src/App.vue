<template>
  <div class="app-shell">
    <h1>Placement Portal</h1>
    <nav>
      <router-link to="/">Home</router-link>
      <router-link to="/login">Login</router-link>
      <router-link to="/drives">Drives</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
</script>
