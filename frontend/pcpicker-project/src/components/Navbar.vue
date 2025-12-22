<template>
  <!-- HomeView 상단 네비 디자인 그대로 전역 네비로 사용 -->
  <header class="top-nav">
    <div class="nav-inner">

      <!-- 로고 -->
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
          <!-- 버튼 → 모달 오픈 -->
          <button class="nav-login" @click="openLoginModal">
            Login
          </button>
          <button class="nav-signup" @click="openRegisterModal">
            Sign Up
          </button>
        </template>
      </div>
    </div>

    <!-- 로그인 모달 -->
    <LoginModal
      v-if="showLoginModal"
      @close="closeLoginModal"
      @logged-in="handleLoggedIn"
      @open-register="openRegisterFromLogin"
    />

    <!-- 회원가입 모달 -->
    <RegisterModal
      v-if="showRegisterModal"
      @close="closeRegisterModal"
      @registered="handleRegistered"
      @open-login="openLoginFromRegister"
    />
  </header>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import AuthService from '@/services/AuthService'
import LoginModal from '@/components/LoginModal.vue'
import RegisterModal from '@/components/RegisterModal.vue'

export default {
  name: 'Navbar',
  components: {
    LoginModal,
    RegisterModal,
  },
  setup() {
    const isAuthenticated = ref(!!AuthService.getCurrentUser())
    const showLoginModal = ref(false)
    const showRegisterModal = ref(false)

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
        // ❌ 여기서도 라우팅 절대 안 함
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    // 모달 관련
    const openLoginModal = () => {
      showRegisterModal.value = false
      showLoginModal.value = true
    }

    const closeLoginModal = () => {
      showLoginModal.value = false
    }

    const openRegisterModal = () => {
      showLoginModal.value = false
      showRegisterModal.value = true
    }

    const closeRegisterModal = () => {
      showRegisterModal.value = false
    }

    const openRegisterFromLogin = () => {
      showLoginModal.value = false
      showRegisterModal.value = true
    }

    const openLoginFromRegister = () => {
      showRegisterModal.value = false
      showLoginModal.value = true
    }

    const handleLoggedIn = () => {
      updateAuthState()      // 네비 상태만 갱신
      showLoginModal.value = false   // 모달만 닫기
      // ❌ router.push('/profile') 같은 거 절대 금지
    }

    const handleRegistered = () => {
      updateAuthState()
      showRegisterModal.value = false
      // ❌ 여기서도 페이지 이동 X
    }

    return {
      isAuthenticated,
      handleLogout,
      showLoginModal,
      showRegisterModal,
      openLoginModal,
      closeLoginModal,
      openRegisterModal,
      closeRegisterModal,
      openRegisterFromLogin,
      openLoginFromRegister,
      handleLoggedIn,
      handleRegistered,
    }
  },
}
</script>

<style scoped>
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

.brand-logo {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.logo-img {
  height: 38px;
  width: auto;
  object-fit: contain;
  cursor: pointer;
}

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

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-login {
  font-size: 14px;
  color: #121212;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px 10px;
}

.nav-login:hover {
  text-decoration: underline;
}

.nav-signup {
  font-size: 14px;
  font-weight: 600;
  padding: 8px 18px;
  border-radius: 999px;
  background-color: #121212;
  color: #ffffff;
  text-decoration: none;
  border: none;
  cursor: pointer;
}

.nav-signup:hover {
  opacity: 0.9;
}

.welcome-text {
  font-size: 13px;
  color: #6a6a6a;
}

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

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
}
</style>
