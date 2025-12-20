<!-- src/views/HomeView.vue -->
<template>
  <div class="home">
    <h1>Welcome to Mr.PCPicker</h1>
    <p v-if="!isAuthenticated">Please <router-link to="/login">login</router-link> or <router-link to="/register">register</router-link> to continue.</p>
    <p v-else>Welcome back! Go to your <router-link to="/profile">profile</router-link>.</p>
  </div>
</template>

<script>
import AuthService from '@/services/AuthService';

export default {
  name: 'HomeView',
  computed: {
    isAuthenticated() {
      return AuthService.getCurrentUser() !== null;
    }
  }
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 20px;
}
</style>