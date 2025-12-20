<!-- src/views/LoginView.vue -->
<template>
  <div class="auth-container">
    <h2>로그인</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>아이디</label>
        <input v-model="username" type="text" :class="{ 'error-input': errors.username }" required />
        <p v-if="errors.username" class="error-message">{{ errors.username }}</p>
      </div>
      <div class="form-group">
        <label>비밀번호</label>
        <div class="password-input-container">
          <input 
            v-model="password" 
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
        <p v-if="errors.password" class="error-message">{{ errors.password }}</p>
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? '로그인 중...' : '로그인' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
      <p>계정이 없으신가요? <router-link to="/register">회원가입하기</router-link></p>
    </form>
  </div>
</template>

<script>
import AuthService from '@/services/AuthService';

export default {
  data() {
    return {
      username: '',
      password: '',
      showPassword: false,
      error: '',
      loading: false,
      errors: {
        username: '',
        password: ''
      }
    };
  },
  methods: {
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword;
    },
    clearErrors() {
      this.error = '';
      this.errors.username = '';
      this.errors.password = '';
    },
    async handleLogin() {
      this.clearErrors();
      this.loading = true;
      
      try {
        await AuthService.login(this.username, this.password);
        this.$router.push('/profile');
      } catch (error) {
        if (error.response && error.response.data) {
          const errorData = error.response.data;
          
          // Handle username error
          if (errorData.username) {
            this.errors.username = errorData.username[0];
          }
          
          // Handle password error
          if (errorData.password) {
            this.errors.password = errorData.password[0];
          }
          
          // Fallback error message
          if (!errorData.username && !errorData.password) {
            this.error = error.response.data.detail || '로그인에 실패했습니다. 다시 시도해주세요.';
          }
        } else {
          this.error = '로그인에 실패했습니다. 다시 시도해주세요.';
          console.error('Login error:', error);
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding-right: 35px; /* Space for the toggle button */
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
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 16px;
  outline: none;
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

.password-toggle:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

button {
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.error {
  color: #ff4444;
  margin: 10px 0;
  text-align: center;
}

.error-message {
  color: #ff4444;
  font-size: 0.85em;
  margin-top: 5px;
  margin-bottom: 0;
}

.error-input {
  border-color: #ff4444 !important;
}

a {
  color: #2196F3;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>