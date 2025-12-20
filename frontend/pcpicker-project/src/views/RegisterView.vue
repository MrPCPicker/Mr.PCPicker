<!-- src/views/RegisterView.vue -->
<template>
  <div class="auth-container">
    <h2>회원가입</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label>이름</label>
        <input v-model="name" type="text" required />
      </div>
      <div class="form-group">
        <label>아이디</label>
        <input v-model="username" type="text" required />
      </div>
      <div class="form-group">
        <label>비밀번호</label>
        <div class="password-input-container">
          <input 
            v-model="password" 
            :type="showPassword ? 'text' : 'password'" 
            required 
          />
          <button 
            type="button" 
            class="password-toggle"
            @click="togglePasswordVisibility('password')"
            :title="showPassword ? '비밀번호 숨기기' : '비밀번호 보기'"
          >
            <span v-if="showPassword">👁️</span>
            <span v-else>👁️‍🗨️</span>
          </button>
        </div>
      </div>
      <div class="form-group">
        <label>비밀번호 확인</label>
        <div class="password-input-container">
          <input 
            v-model="password2" 
            :type="showPassword2 ? 'text' : 'password'" 
            required 
          />
          <button 
            type="button" 
            class="password-toggle"
            @click="togglePasswordVisibility('password2')"
            :title="showPassword2 ? '비밀번호 숨기기' : '비밀번호 보기'"
          >
            <span v-if="showPassword2">👁️</span>
            <span v-else>👁️‍🗨️</span>
          </button>
        </div>
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? '가입 중...' : '가입하기' }}
      </button>
      <div v-if="error" class="error">
        <p v-if="error.detail">{{ error.detail }}</p>
        <template v-else>
          <p v-for="(errors, field) in error" :key="field">
            {{ field }}: {{ Array.isArray(errors) ? errors[0] : errors }}
          </p>
        </template>
      </div>
      <p>이미 계정이 있으신가요? <router-link to="/login">로그인하기</router-link></p>
    </form>
  </div>
</template>

<script>
import AuthService from '@/services/AuthService';

export default {
  data() {
    return {
      name: '',
      username: '',
      password: '',
      password2: '',
      showPassword: false,
      showPassword2: false,
      error: null,
      loading: false
    };
  },
  methods: {
    togglePasswordVisibility(field) {
      if (field === 'password') {
        this.showPassword = !this.showPassword;
      } else if (field === 'password2') {
        this.showPassword2 = !this.showPassword2;
      }
    },
    async handleRegister() {
      if (this.password !== this.password2) {
        this.error = { password: ["비밀번호가 일치하지 않습니다."] };
        return;
      }

      this.loading = true;
      this.error = null;

      try {
        const response = await AuthService.register(
          this.name,
          this.username,
          this.password
        );
        
        // If registration is successful and tokens are returned
        if (response.data && response.data.tokens) {
          // Save tokens to local storage
          const userData = {
            access: response.data.tokens.access,
            refresh: response.data.tokens.refresh,
            user: response.data.user
          };
          localStorage.setItem('user', JSON.stringify(userData));
          
          // Dispatch storage event to update auth state in Navbar
          window.dispatchEvent(new Event('storage'));
          
          // Redirect to home page
          this.$router.push('/');
        } else {
          // Fallback to login page if no tokens are returned
          this.$router.push('/login');
        }
      } catch (error) {
        this.error = error.response?.data || { detail: '회원가입에 실패했습니다. 다시 시도해주세요.' };
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Same styles as LoginView */
.auth-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-container input {
  width: 100%;
  padding-right: 35px; /* Space for the toggle button */
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
  color: red;
  margin-top: 10px;
}

a {
  color: #2196F3;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>