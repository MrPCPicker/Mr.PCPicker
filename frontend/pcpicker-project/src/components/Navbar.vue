<template>
  <nav>
    <div class="nav-content">
      <router-link to="/" class="logo">PCPicker</router-link>
      <div class="nav-links">
        <router-link to="/" class="nav-link">Home</router-link>

        <template v-if="isAuthenticated">
          <router-link to="/profile" class="nav-link">Profile</router-link>
          <button @click="handleLogout" class="logout-btn">Logout</button>
        </template>

        <template v-else>
          <router-link to="/login" class="nav-link">Login</router-link>
          <router-link to="/register" class="nav-link">Register</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import AuthService from '@/services/AuthService';

export default {
  name: 'Navbar',
  setup() {
    const router = useRouter();

    // 로그인 여부 상태
    const isAuthenticated = ref(!!AuthService.getCurrentUser());

    const updateAuthState = () => {
      isAuthenticated.value = !!AuthService.getCurrentUser();
      console.log('auth state changed:', isAuthenticated.value);
    };

    onMounted(() => {
      // 같은 탭: auth-changed, 다른 탭: storage
      window.addEventListener('auth-changed', updateAuthState);
      window.addEventListener('storage', updateAuthState);
      // 초기 한 번 동기화
      updateAuthState();
    });

    onUnmounted(() => {
      window.removeEventListener('auth-changed', updateAuthState);
      window.removeEventListener('storage', updateAuthState);
    });

    const handleLogout = async () => {
      try {
        await AuthService.logout();   // 여기서 localStorage 비우고 auth-changed 발생
        updateAuthState();            // 혹시 몰라 한 번 더 동기화
        router.push('/login');
      } catch (error) {
        console.error('Logout error:', error);
      }
    };

    return {
      isAuthenticated,
      handleLogout,
    };
  },
};
</script>

<style scoped>
nav {
  background: #333;
  padding: 1rem 0;
  color: white;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-links a.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  font-weight: 500;
}

.nav-links a.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  text-decoration: none;
}

.nav-links a.router-link-active {
  background: rgba(255, 255, 255, 0.1);
}

.logout-btn {
  background: #f44336;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn:hover {
  background: #d32f2f;
}
</style>
