<template>
  <div class="home">
    <Header />

    <!-- Hero Section -->
    <section class="hero-wrapper">
      <h1 class="hero-title">
        Welcome to<br />
        MR.PCPICKER
      </h1>

      <p class="hero-desc">
        PC 추천 서비스<br />
        <br />
        made by 이주선, 양새하
      </p>

      <SearchBar />
    </section>
  </div>
</template>

<script setup>
import Header from '@/components/Header.vue'
import SearchBar from '@/components/SearchBar.vue'
</script>

<style>

</style>