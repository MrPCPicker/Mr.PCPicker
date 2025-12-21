<template>
  <div id="app">
    <!-- 모든 페이지에서 공통으로 보이는 네비게이션 바 -->
    <Navbar />

    <!-- 여기에서만 페이지 내용이 바뀜 -->
    <router-view />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue'

export default {
  name: 'App',
  components: {
    Navbar
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
}
</style>
