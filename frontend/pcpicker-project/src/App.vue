<template>
  <Header />

  <RouterView />

  <!-- ⭐ 전역 로그인 모달 -->
  <LoginModal
    v-if="isLoginOpen"
    @close="closeLogin"
  />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import Header from '@/components/Header.vue'
import LoginModal from '@/components/LoginModal.vue'

const route = useRoute()
const router = useRouter()

// URL이 /login이면 모달 ON
const isLoginOpen = computed(() => route.path === '/login')

function closeLogin() {
  router.back()
}
</script>
