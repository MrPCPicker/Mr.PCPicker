<template>
  <header class="top-nav">
    <div class="nav-inner">

      <router-link to="/" class="brand-logo">
        <img
          src="@/assets/logo_transparent.png"
          alt="Mr.PC Picker Logo"
          class="logo-img"
        />
      </router-link>

      <nav class="nav-links">
        <router-link to="/" class="nav-link" exact>Home</router-link>
        <router-link to="/community" class="nav-link">Community</router-link>
        <router-link to="/search" class="nav-link">Search</router-link>
      </nav>

      <div class="nav-actions">
        <template v-if="isAuthenticated">
          <span class="welcome-text">Welcome back, {{ userName }}님 👋</span>
          <router-link to="/cart" class="cart-icon">
            🧺
            <!-- 🛒 -->
          </router-link>
          <router-link to="/profile" class="nav-signup">My Page</router-link>
          <button class="nav-logout-btn" @click="handleLogout">
            Logout
          </button>
        </template>

        <template v-else>
          <button class="nav-login" @click="openLoginModal">
            Login
          </button>
          <button class="nav-signup" @click="openRegisterModal">
            Sign Up
          </button>
        </template>
      </div>
    </div>

    <LoginModal
      v-if="showLoginModal"
      @close="closeLoginModal"
      @logged-in="handleLoggedIn"
      @open-register="openRegisterFromLogin"
    />

    <RegisterModal
      v-if="showRegisterModal"
      @close="closeRegisterModal"
      @registered="handleRegistered"
      @open-login="openLoginFromRegister"
    />
  </header>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router' // 💡 router 이동을 위해 추가
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
    const router = useRouter() // 💡 router 인스턴스 생성
    const isAuthenticated = ref(!!AuthService.getCurrentUser())
    const currentUserData = ref(AuthService.getCurrentUser())
    const showLoginModal = ref(false)
    const showRegisterModal = ref(false)

    // 이름을 추출하는 Computed 속성
    const userName = computed(() => {
      if (!currentUserData.value) return ''
      const user = currentUserData.value.user || currentUserData.value
      return user.name || user.username || 'User'
    })

    const updateAuthState = () => {
      const user = AuthService.getCurrentUser()
      isAuthenticated.value = !!user
      currentUserData.value = user
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
        // 💡 로그아웃 성공 후 홈화면으로 자동 이동
        router.push('/')
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    // 모달 관련 로직
    const openLoginModal = () => {
      showRegisterModal.value = false
      showLoginModal.value = true
    }
    const closeLoginModal = () => { showLoginModal.value = false }
    const openRegisterModal = () => {
      showLoginModal.value = false
      showRegisterModal.value = true
    }
    const closeRegisterModal = () => { showRegisterModal.value = false }
    const openRegisterFromLogin = () => {
      showLoginModal.value = false
      showRegisterModal.value = true
    }
    const openLoginFromRegister = () => {
      showRegisterModal.value = false
      showLoginModal.value = true
    }
    const handleLoggedIn = () => {
      updateAuthState()
      showLoginModal.value = false
    }
    const handleRegistered = () => {
      updateAuthState()
      showRegisterModal.value = false
    }

    // Cart functionality
    const cartItemCount = ref(0)
    
    const updateCartCount = () => {
      const cart = JSON.parse(localStorage.getItem('cart') || '[]')
      cartItemCount.value = cart.reduce((total, item) => total + (item.quantity || 1), 0)
    }
    
    onMounted(() => {
      updateCartCount()
      window.addEventListener('storage', updateCartCount)
      window.addEventListener('cart-updated', updateCartCount)
    })
    
    onUnmounted(() => {
      window.removeEventListener('storage', updateCartCount)
      window.removeEventListener('cart-updated', updateCartCount)
    })

    return {
      isAuthenticated,
      userName,
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

/* Cart Icon Styles */
.cart-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #2f3a45;
  text-decoration: none;
  padding: 0 8px;
  transition: transform 0.2s;
}

.cart-icon:hover {
  transform: scale(1.1);
  color: #1e6fd7;
}

.cart-count {
  position: absolute;
  top: -2px;
  right: -2px;
  background-color: #ff4d4f;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  border: 2px solid #ffffff;
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
}
</style>