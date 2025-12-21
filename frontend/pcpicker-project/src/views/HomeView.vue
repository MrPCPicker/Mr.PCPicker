<!-- src/views/HomeView.vue -->
<template>
  <div class="home">
    <!-- Top Navigation -->
    <header class="top-nav">
      <div class="nav-inner">
        <router-link to="/" class="brand">
          <span class="brand-main">Mr.</span>
          <span class="brand-accent">PC</span>
          <span class="brand-sub">Picker</span>
        </router-link>

        <nav class="nav-links">
          <router-link to="/" class="nav-link" exact>Home</router-link>
          <router-link to="/community" class="nav-link">Community</router-link>
        </nav>

        <div class="nav-actions">
          <template v-if="!isAuthenticated">
            <router-link to="/login" class="nav-login">Login</router-link>
            <router-link to="/register" class="nav-signup">Sign Up</router-link>
          </template>
          <template v-else>
            <span class="welcome-text">Welcome back 👋</span>
            <router-link to="/profile" class="nav-signup">My Page</router-link>
          </template>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <main>
      <section class="hero">
        <div class="hero-inner">
          <div class="hero-copy">
            <h1 class="hero-title">
              Build the right PC<br />
              for your needs
            </h1>
            <p class="hero-desc">
              스펙 비교부터 추천까지, Mr.PC Picker가<br />
              당신에게 가장 잘 맞는 데스크탑·노트북 구성을 찾아드립니다.
            </p>

            <div class="hero-search">
              <SearchBar />
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import AuthService from '@/services/AuthService'
import SearchBar from '@/components/SearchBar.vue'

export default {
  name: 'HomeView',
  components: { SearchBar },
  computed: {
    isAuthenticated() {
      return AuthService.getCurrentUser() !== null
    }
  }
}
</script>

<style scoped>
/* ----- Layout ----- */
.home {
  min-height: 100vh;
  background-color: #ffffff;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
    sans-serif;
}

/* ----- Top Nav ----- */
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

/* Brand */
.brand {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  text-decoration: none;
}
.brand-main {
  font-weight: 700;
  font-size: 20px;
  color: #121212;
}
.brand-accent {
  font-weight: 800;
  font-size: 20px;
  color: #e12726;
}
.brand-sub {
  font-weight: 500;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6a6a6a;
}

/* Nav links */
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

/* Nav actions */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
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

/* ----- HERO (메인) ----- */
/* 풀블리드(화면 가로 100%) + 네비 아래부터 다 어둡게 */
.hero {
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;   /* 부모의 max-width와 상관없이 화면 전체로 */
  margin-right: -50vw;
  width: 100vw;

  background-color: #2f3a45;
  min-height: calc(100vh - 72px); /* 네비 높이 제외한 전체 높이 */
  display: flex;
  justify-content: center;
}

.hero-inner {
  width: 100%;
  padding: 96px 48px 120px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.hero-copy {
  text-align: left;
}

.hero-title {
  font-size: 40px;
  line-height: 1.2;
  color: #ffffff;
  margin-bottom: 16px;
  font-weight: 700;
}

.hero-desc {
  font-size: 15px;
  line-height: 1.6;
  color: #d9d9d9;
  margin-bottom: 32px;
}

/* 검색 바 pill 스타일 래퍼 */
.hero-search {
  background-color: #f4f6fa;
  border-radius: 999px;
  padding: 10px 20px;
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
}

/* SearchBar가 안에서 꽉 차게 */
.hero-search :deep(*) {
  width: 100%;
}

/* ----- Responsive ----- */
@media (max-width: 768px) {
  .nav-inner {
    padding-inline: 16px;
  }

  .nav-links {
    display: none;
  }

  .hero {
    min-height: auto;
    margin-left: 0;
    margin-right: 0;
    width: 100%;
  }

  .hero-inner {
    padding: 56px 16px 72px;
    justify-content: center;
  }

  .hero-copy {
    max-width: 100%;
    text-align: center;
  }

  .hero-title {
    font-size: 30px;
  }

  .hero-search {
    margin: 0 auto;
  }
}
</style>
