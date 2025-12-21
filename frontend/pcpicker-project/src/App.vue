<template>
  <div id="app">
    <!-- 네비 제거됨 -->
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
  text-align: left; /* center -> left 로 UI 맞춤 */
  color: #2c3e50;
}

/* 기존 nav, a 스타일 삭제됨 */
</style>
