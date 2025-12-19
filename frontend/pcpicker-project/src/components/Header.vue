<template>
  <header class="header">
    <div class="header-left">MR.PCPICKER</div>

    <nav class="header-nav">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/community">Community</RouterLink>
      <RouterLink to="/profile">My Profile</RouterLink>
    </nav>

    <RouterLink to="/login" class="header-login">
      Login
    </RouterLink>
  </header>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
