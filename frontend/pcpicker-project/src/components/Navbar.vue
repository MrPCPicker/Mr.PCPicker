<template>
  <!-- HomeView 상단 네비 디자인 그대로 전역 네비로 사용 -->
  <header class="top-nav">
    <div class="nav-inner">

      <!-- 로고를 이미지로 교체 -->
      <router-link to="/" class="brand-logo">
        <img
          src="@/assets/logo_transparent.png"
          alt="Mr.PC Picker Logo"
          class="logo-img"
        />
      </router-link>

      <!-- 가운데 네비게이션 링크 -->
      <nav class="nav-links">
        <router-link to="/" class="nav-link" exact>Home</router-link>
        <router-link to="/community" class="nav-link">Community</router-link>
      </nav>

      <!-- 오른쪽 액션 영역 -->
      <div class="nav-actions">
        <template v-if="isAuthenticated">
          <span class="welcome-text">Welcome back 👋</span>
          <router-link to="/profile" class="nav-signup">My Page</router-link>
          <button class="nav-logout-btn" @click="handleLogout">
            Logout
          </button>
        </template>

        <template v-else>
          <router-link to="/login" class="nav-login">Login</router-link>
          <router-link to="/register" class="nav-signup">Sign Up</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AuthService from '@/services/AuthService'

export default {
  name: 'Navbar',
  setup() {
    const router = useRouter()

    const isAuthenticated = ref(!!AuthService.getCurrentUser())

    const updateAuthState = () => {
      isAuthenticated.value = !!AuthService.getCurrentUser()
    }

    onMounted(() => {
      window.addEventListener('auth-changed', updateAuthState)
      window.addEventListener('storage', updateAuthState)
      updateAuthState()
    })

    onUnmounted(() => {
      window.removeEventListener('auth-changed', updateAuthState)
      window.removeEventListener('storage', updateAuthState)
    })

    const handleLogout = async () => {
      try {
        await AuthService.logout()
        updateAuthState()
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    return {
      isAuthenticated,
      handleLogout
    }
  }
}
</script>

<style scoped>
/* ----- Top Nav (HomeView 디자인 차용) ----- */
.top-nav {
  background-color: #ffffff;
  border-bottom: 1px solid #f0f2f5;
}

.nav-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Brand Logo Area */
.brand-logo {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.logo-img {
  height: 38px;        /* 원하는 크기로 조절 가능 */
  width: auto;
  object-fit: contain;
  cursor: pointer;
}

/* Nav links (가운데) */
.nav-links {
  display: flex;
  gap: 24px;
  flex: 1;
  justify-content: center;
}

.nav-link {
  font-size: 14px;
  text-decoration: none;
  color: #6a6a6a;
}

.nav-link.router-link-exact-active {
  color: #1e6fd7;
}

/* 오른쪽 액션 */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-login {
  font-size: 14px;
  color: #121212;
  text-decoration: none;
}
.nav-signup {
  font-size: 14px;
  font-weight: 600;
  padding: 8px 18px;
  border-radius: 999px;
  background-color: #121212;
  color: #ffffff;
  text-decoration: none;
}

.nav-signup:hover {
  opacity: 0.9;
}

.welcome-text {
  font-size: 13px;
  color: #6a6a6a;
}

/* Logout 버튼 */
.nav-logout-btn {
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background-color: #ffffff;
  color: #6b7280;
  cursor: pointer;
}

.nav-logout-btn:hover {
  background-color: #f3f4f6;
  border-color: #d1d5db;
  color: #111827;
}

/* 반응형 */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
}
</style>
