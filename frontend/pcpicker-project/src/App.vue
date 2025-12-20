<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <template v-if="isAuthenticated">
        <router-link to="/profile">Profile</router-link> |
        <a href="#" @click.prevent="handleLogout">Logout</a>
      </template>
      <template v-else>
        <router-link to="/login">Login</router-link> |
        <router-link to="/register">Register</router-link>
      </template>
    </nav>
    <router-view />
  </div>
</template>

<script>
import AuthService from '@/services/AuthService';

export default {
  name: 'App',
  computed: {
    isAuthenticated() {
      return AuthService.getCurrentUser() !== null;
    }
  },
  methods: {
    async handleLogout() {
      try {
        await AuthService.logout();
        this.$router.push('/login');
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  margin: 0 10px;
  text-decoration: none;
}

nav a.router-link-exact-active {
  color: #42b983;
}

button {
  cursor: pointer;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  margin: 5px;
}

button:hover {
  opacity: 0.9;
}

.error {
  color: #f44336;
  margin: 10px 0;
}
</style>