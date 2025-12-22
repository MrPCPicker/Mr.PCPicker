<!-- src/components/RegisterModal.vue -->
<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2 class="modal-title">회원가입</h2>

      <form @submit.prevent="handleRegister">
        <!-- 이름 -->
        <div class="form-group">
          <label>이름</label>
          <input
            v-model="formData.name"
            type="text"
            :class="{ 'error-input': errors.name }"
            required
          />
          <p v-if="errors.name" class="error-message">
            {{ errors.name }}
          </p>
        </div>

        <!-- 아이디 -->
        <div class="form-group">
          <label>아이디</label>
          <input
            v-model="formData.username"
            type="text"
            :class="{ 'error-input': errors.username }"
            required
          />
          <p v-if="errors.username" class="error-message">
            {{ errors.username }}
          </p>
        </div>

        <!-- 이메일 -->
        <div class="form-group">
          <label>이메일</label>
          <input
            v-model="formData.email"
            type="email"
            :class="{ 'error-input': errors.email }"
            required
          />
          <p v-if="errors.email" class="error-message">
            {{ errors.email }}
          </p>
        </div>

        <!-- 비밀번호 -->
        <div class="form-group">
          <label>비밀번호</label>
          <div class="password-input-container">
            <input
              v-model="formData.password"
              :type="showPassword ? 'text' : 'password'"
              :class="{ 'error-input': errors.password }"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="togglePasswordVisibility"
              :title="showPassword ? '비밀번호 숨기기' : '비밀번호 보기'"
            >
              <span v-if="showPassword">👁️</span>
              <span v-else>👁️‍🗨️</span>
            </button>
          </div>
          <p v-if="errors.password" class="error-message">
            {{ errors.password }}
          </p>
        </div>

        <!-- 비밀번호 확인 -->
        <div class="form-group">
          <label>비밀번호 확인</label>
          <div class="password-input-container">
            <input
              v-model="formData.password2"
              :type="showPassword2 ? 'text' : 'password'"
              :class="{ 'error-input': errors.password2 }"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="togglePasswordVisibility2"
              :title="showPassword2 ? '비밀번호 숨기기' : '비밀번호 보기'"
            >
              <span v-if="showPassword2">👁️</span>
              <span v-else>👁️‍🗨️</span>
            </button>
          </div>
          <p v-if="errors.password2" class="error-message">
            {{ errors.password2 }}
          </p>
        </div>

        <p v-if="error" class="error">
          {{ error }}
        </p>

        <button type="submit" :disabled="loading">
          {{ loading ? '가입 중...' : '가입하기' }}
        </button>

        <p class="auth-footer">
          이미 계정이 있으신가요?
          <button class="auth-link-button" @click.prevent="goLogin">
            로그인하기
          </button>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AuthService from '@/services/AuthService'

const emit = defineEmits(['close', 'registered', 'open-login'])

const formData = ref({
  name: '',
  username: '',
  email: '',
  password: '',
  password2: '',
})
const showPassword = ref(false)
const showPassword2 = ref(false)
const loading = ref(false)
const error = ref(null)
const errors = ref({
  name: '',
  username: '',
  email: '',
  password: '',
  password2: '',
})

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const togglePasswordVisibility2 = () => {
  showPassword2.value = !showPassword2.value
}

const clearErrors = () => {
  error.value = null
  errors.value = {
    name: '',
    username: '',
    email: '',
    password: '',
    password2: '',
  }
}

const goLogin = () => {
  emit('close')
  emit('open-login')
}

const handleRegister = async () => {
  clearErrors()

  if (formData.value.password !== formData.value.password2) {
    errors.value.password2 = '비밀번호가 일치하지 않습니다.'
    return
  }

  loading.value = true

  try {
    await AuthService.register(formData.value)
    window.dispatchEvent(new Event('auth-changed'))
    emit('registered')
    emit('close')
  } catch (err) {
    if (err.response && err.response.data) {
      const data = err.response.data

      if (data.name) {
        errors.value.name = Array.isArray(data.name)
          ? data.name[0]
          : data.name
      }
      if (data.username) {
        errors.value.username = Array.isArray(data.username)
          ? data.username[0]
          : data.username
      }
      if (data.email) {
        errors.value.email = Array.isArray(data.email)
          ? data.email[0]
          : data.email
      }
      if (data.password) {
        errors.value.password = Array.isArray(data.password)
          ? data.password[0]
          : data.password
      }
      if (data.password2) {
        errors.value.password2 = Array.isArray(data.password2)
          ? data.password2[0]
          : data.password2
      }

      if (
        !data.name &&
        !data.username &&
        !data.email &&
        !data.password &&
        !data.password2
      ) {
        error.value =
          data.detail || '회원가입에 실패했습니다. 다시 시도해주세요.'
      }
    } else {
      error.value = '회원가입에 실패했습니다. 다시 시도해주세요.'
      console.error('Register error (modal):', err)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

/* ⇩ 카드 배경 흰색 */
.modal {
  max-width: 420px;
  width: 90%;
  background: #ffffff;
  border-radius: 20px;
  padding: 28px 24px 24px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
  border: 1px solid #e5e7eb;
  color: #111827;
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 18px;
  text-align: center;
  color: #111827;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-size: 0.9rem;
  color: #374151;
}

/* ⇩ 입력란 흰색 */
.form-group input {
  width: 100%;
  padding: 9px 10px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background-color: #ffffff;
  color: #111827;
  font-size: 0.92rem;
  padding-right: 38px;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease,
    background-color 0.15s ease;
}

.form-group input::placeholder {
  color: #9ca3af;
}

.form-group input:focus {
  outline: none;
  border-color: #6b5fcf;
  box-shadow: 0 0 0 1px rgba(107, 95, 207, 0.25);
}

.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-toggle {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 16px;
  outline: none;
  width: 24px;
  height: 24px;
  border-radius: 6px;
}

.password-toggle:hover {
  background-color: rgba(243, 244, 246, 0.8);
}

button[type='submit'] {
  width: 100%;
  padding: 10px 0;
  background-color: #6b5fcf;
  color: #f9fafb;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  margin-top: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  transition:
    background-color 0.15s ease,
    transform 0.08s ease,
    box-shadow 0.15s ease;
}

button[type='submit']:hover:enabled {
  background-color: #7c6fff;
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(107, 95, 207, 0.35);
}

button[type='submit']:disabled {
  opacity: 0.7;
  cursor: default;
  box-shadow: none;
}

.error {
  color: #b91c1c;
  margin: 8px 0 4px;
  text-align: center;
  font-size: 0.9rem;
}

.error-message {
  color: #b91c1c;
  font-size: 0.8em;
  margin-top: 4px;
  margin-bottom: 0;
}

.error-input {
  border-color: #f97373 !important;
}

.auth-footer {
  margin-top: 12px;
  text-align: center;
  font-size: 0.88rem;
  color: #6b7280;
}

.auth-link-button {
  background: none;
  border: none;
  color: #4f46e5;
  cursor: pointer;
  margin-left: 4px;
  padding: 0;
  font-size: 0.88rem;
}

.auth-link-button:hover {
  text-decoration: underline;
}

a {
  color: #4f46e5;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
