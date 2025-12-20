// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import AuthService from '@/services/AuthService'
import HomeView from '@/views/HomeView.vue'
import CommunityView from '@/views/CommunityView.vue'
import ProfileView from '@/views/ProfileView.vue'
import LoginView from '@/views/LoginView.vue'

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
    }
  ],
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = AuthService.getCurrentUser() !== null;
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    next('/profile');
  } else {
    next();
  }
});

export default router;