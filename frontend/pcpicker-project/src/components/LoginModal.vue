<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2 class="modal-title">Login</h2>

      <input type="email" placeholder="Email" />
      <input type="password" placeholder="Password" />

      <button class="header-login" style="width: 100%; margin-top: 12px;">
        Login
      </button>

      <p style="margin-top: 14px; text-align: center;">Sign Up</p>
    </div>
  </div>
</template>

<script setup>
defineEmits(['close'])
</script>
