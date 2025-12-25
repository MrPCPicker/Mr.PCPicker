<template>
  <div class="register-view">
    <RegisterModal 
      :show="true" 
      @close="handleClose" 
      @registered="handleRegistered"
      @open-login="handleOpenLogin"
    />
  </div>
</template>

<script>
import RegisterModal from '@/components/RegisterModal.vue'
import { useRouter } from 'vue-router'

export default {
  name: 'RegisterView',
  components: {
    RegisterModal
  },
  setup() {
    const router = useRouter()

    const handleClose = () => {
      router.push('/')
    }

    const handleRegistered = () => {
      // Optionally handle successful registration
      router.push('/login')
    }

    const handleOpenLogin = () => {
      router.push('/login')
    }

    return {
      handleClose,
      handleRegistered,
      handleOpenLogin
    }
  }
}
</script>

<style scoped>
.register-view {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  padding: 20px;
}
</style>
