import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // access token 존재 여부로 로그인 판단
  const user = ref(JSON.parse(localStorage.getItem('user')))

  const isAuthenticated = computed(() => {
    return !!(user.value && user.value.access)
  })

  function setUser(newUser) {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  function clearUser() {
    user.value = null
    localStorage.removeItem('user')
  }

  return {
    user,
    isAuthenticated,
    setUser,
    clearUser,
  }
})
