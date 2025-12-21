// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import AuthService from '@/services/AuthService'
import HomeView from '@/views/HomeView.vue'
import CommunityView from '@/views/CommunityView.vue'
import ProfileView from '@/views/ProfileView.vue'
import LoginView from '@/views/LoginView.vue'
import RecommendView from '@/views/RecommendView.vue'   // 🔹 새로 추가

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { 
      path: '/', 
      name: 'home',
      component: HomeView 
    },
    { 
      path: '/community', 
      name: 'community',
      component: CommunityView 
    },
    { 
      path: '/profile', 
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    { 
      path: '/login', 
      name: 'login', 
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/recommend',
      name: 'Recommend',                // 🔹 SearchBar.vue 에서 쓰는 name
      component: RecommendView,
      meta: { requiresAuth: false }
    }
  ],
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = AuthService.getCurrentUser() !== null
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // 보호된 페이지인데 로그인 안 됐으면 로그인으로
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    // 이미 로그인했는데 로그인/회원가입으로 가면 프로필로 보냄
    next('/profile')
  } else {
    next()
  }
})

export default router
