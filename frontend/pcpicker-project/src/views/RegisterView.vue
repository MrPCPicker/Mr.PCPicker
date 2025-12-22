<template>
  <div class="profile-container">
    <form>
    <h2 class="title">프로필 정보</h2>

    <div v-if="user" class="profile-card">
      <!-- 프로필 이미지 -->
      <div class="avatar">
        <img
          :src="user.profile_image || defaultAvatar"
          alt="profile"
        />
      </div>

      <!-- 아이디 -->
      <div class="field">
        <label>아이디</label>
        <input type="text" :value="user.username" disabled />
      </div>

      <!-- 이름 -->
      <div class="field">
        <label>이름</label>
        <input v-model="updateForm.name" type="text" />
      </div>

      <!-- 이메일 -->
      <div class="field">
        <label>이메일</label>
        <input v-model="updateForm.email" type="email" />

        <!-- 비밀번호 확인 -->
        <div class="form-group">
          <label for="password2">비밀번호 확인</label>
          <div class="password-input">
            <input 
              id="password2"
              :type="showPassword2 ? 'text' : 'password'"
              v-model="formData.password2"
              class="form-input"
              required
            />
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

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '처리 중...' : '가입하기' }}
        </button>

        <div class="auth-footer">
          이미 계정이 있으신가요? 
          <router-link to="/login" class="auth-link">로그인하기</router-link>
        </div>
      </form>
  </div>
</template>

<script>
import AuthService from '@/services/AuthService';
import { formToJSON } from 'axios';

export default {
  name: 'RegisterView',
  data() {
    return {
      formData: {
        name: '',
        username: '',
        email: '',
        password: '',
        password2: ''
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
        this.updateForm.name = res.data.name || ''
        this.updateForm.email = res.data.email || ''
      } catch (err) {
        if (err.response?.status === 401) {
          this.$router.push('/login')
        }
      }
    },

    async handleUpdate() {
      try {
        await AuthService.updateProfile(this.updateForm)
        this.updateError = ''
        await this.loadUserProfile()
        alert('프로필이 저장되었습니다.')
      } catch (err) {
        this.updateError = '프로필 수정에 실패했습니다.'
      }
    },

    handleLogout() {
      AuthService.logout()
      this.$router.push('/login')
    },

    async handleDeleteAccount() {
      if (!confirm('정말 탈퇴하시겠습니까?')) return
      await AuthService.deleteAccount()
      this.$router.push('/')
    },
  },
}
</script>

<style scoped>
.profile-container {
  max-width: 500px;
  margin: 40px auto;
}

.title {
  text-align: center;
  margin-bottom: 20px;
}

.profile-card {
  background: #fff;
  padding: 30px;
  border-radius: 12px;
}

.avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
}

.field {
  margin-bottom: 14px;
}

.field label {
  display: block;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.field input {
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ddd;
}

.save-btn {
  width: 100%;
  margin-top: 20px;
  padding: 12px;
  background: #111;
  color: #fff;
  border-radius: 8px;
}

.actions {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
}

.danger {
  background: #e53935;
  color: #fff;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
