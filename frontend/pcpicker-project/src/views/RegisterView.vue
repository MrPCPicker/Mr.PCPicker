<template>
  <div class="register-container">
    <h2>회원가입</h2>
    
    <form @submit.prevent="handleRegister" class="register-form">
      <!-- 아이디 -->
      <div class="form-group">
        <label for="username">아이디</label>
        <input 
          id="username"
          v-model="formData.username"
          type="text" 
          required
          placeholder="아이디를 입력하세요"
          class="form-input"
        >
      </div>

      <!-- 비밀번호 -->
      <div class="form-group">
        <label for="password1">비밀번호</label>
        <div class="password-input">
          <input 
            id="password1"
            :type="showPassword ? 'text' : 'password'"
            v-model="formData.password1"
            required
            placeholder="비밀번호를 입력하세요"
            class="form-input"
          >
          <button 
            type="button" 
            class="toggle-password"
            @click="togglePasswordVisibility"
          >
            <span v-if="showPassword">👁️</span>
            <span v-else>👁️‍🗨️</span>
          </button>
        </div>
      </div>

      <!-- 비밀번호 확인 -->
      <div class="form-group">
        <label for="password2">비밀번호 확인</label>
        <div class="password-input">
          <input 
            id="password2"
            :type="showPassword2 ? 'text' : 'password'"
            v-model="formData.password2"
            required
            placeholder="비밀번호를 다시 입력하세요"
            class="form-input"
          >
          <button 
            type="button" 
            class="toggle-password"
            @click="togglePasswordVisibility2"
          >
            <span v-if="showPassword2">👁️</span>
            <span v-else>👁️‍🗨️</span>
          </button>
        </div>
      </div>

      <!-- 이름 -->
      <div class="form-group">
        <label for="name">이름</label>
        <input 
          id="name"
          v-model="formData.name" 
          type="text" 
          required
          placeholder="이름을 입력하세요"
          class="form-input"
        >
      </div>

      <!-- 이메일 -->
      <div class="form-group">
        <label for="email">이메일</label>
        <input 
          id="email"
          v-model="formData.email" 
          type="email" 
          required
          placeholder="이메일을 입력하세요"
          class="form-input"
        >
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <button type="submit" class="submit-btn" :disabled="loading">
        {{ loading ? '처리 중...' : '가입하기' }}
      </button>
    </form>

    <div class="auth-footer">
      이미 계정이 있으신가요? 
      <router-link to="/login" class="auth-link">로그인하기</router-link>
    </div>
  </div>
</template>

<script>
import { auth } from '@/services/api';

export default {
  name: 'RegisterView',
  data() {
    return {
      formData: {
        username: '',
        password1: '',
        password2: '',
        name: '',
        email: ''
      },
      showPassword: false,
      showPassword2: false,
      loading: false,
      error: null
    };
  },
  methods: {
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword;
    },
    togglePasswordVisibility2() {
      this.showPassword2 = !this.showPassword2;
    },
    async handleRegister() {
      // 비밀번호 일치 확인
      if (this.formData.password1 !== this.formData.password2) {
        this.error = '비밀번호가 일치하지 않습니다.';
        return;
      }

      this.loading = true;
      this.error = null;

      try {
        const registrationData = {
          username: this.formData.username,
          password: this.formData.password1,  // Changed to match backend's expected field name
          password2: this.formData.password2,
          name: this.formData.name,
          email: this.formData.email
        };
        
        console.log('Sending registration data:', registrationData);
        
        const response = await auth.register(registrationData);
        console.log('Registration successful:', response.data);

        // 회원가입 성공 시 로그인 페이지로 리다이렉트
        this.$router.push('/login');
        
      } catch (error) {
        console.error('회원가입 오류:', error);
        if (error.response && error.response.data) {
          console.error('Error details:', error.response.data);
          // Show the first error message from the server
          const errorData = error.response.data;
          if (typeof errorData === 'object') {
            // Get the first error message from the response
            const firstErrorKey = Object.keys(errorData)[0];
            const firstErrorMessage = Array.isArray(errorData[firstErrorKey]) 
              ? errorData[firstErrorKey][0] 
              : errorData[firstErrorKey];
            this.error = `${firstErrorKey}: ${firstErrorMessage}`;
          } else {
            this.error = errorData.toString();
          }
        }
        if (error.response) {
          // 서버에서 에러 응답이 온 경우
          if (error.response.data) {
            // 에러 메시지가 객체 형태로 오는 경우 처리
            const errorData = error.response.data;
            if (typeof errorData === 'object') {
              this.error = Object.values(errorData).flat().join('\n');
            } else {
              this.error = errorData.toString();
            }
          } else {
            this.error = '회원가입 중 오류가 발생했습니다.';
          }
        } else if (error.request) {
          // 요청이 전송되었지만 응답을 받지 못한 경우
          this.error = '서버로부터 응답을 받지 못했습니다. 네트워크 연결을 확인해주세요.';
        } else {
          // 요청을 보내기 전에 발생한 오류
          this.error = '요청을 처리하는 중 오류가 발생했습니다.';
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.register-container {
  max-width: 500px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 500;
  color: #444;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-input:focus {
  border-color: #4a90e2;
  outline: none;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.password-input {
  position: relative;
  display: flex;
  align-items: center;
}

.toggle-password {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-size: 1.2rem;
  color: #666;
}

.submit-btn {
  background-color: #4a90e2;
  color: white;
  padding: 0.8rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  margin-top: 1rem;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #357abd;
}

.submit-btn:disabled {
  background-color: #a0c4ff;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
}

.auth-link {
  color: #4a90e2;
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.5rem;
}

.auth-link:hover {
  text-decoration: underline;
}

</style>
