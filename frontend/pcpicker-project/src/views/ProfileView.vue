<template>
  <div class="profile-container">
    <h2>프로필</h2>
    <div v-if="user">
      <div class="profile-info">
        <p><strong>이름:</strong> {{ user.name || '이름이 없습니다' }}</p>
      </div>

      <div class="profile-actions">
        <button @click="showUpdateForm = !showUpdateForm">
          {{ showUpdateForm ? 'Cancel' : 'Update Profile' }}
        </button>
        <button @click="showPasswordForm = !showPasswordForm">
          {{ showPasswordForm ? 'Cancel' : 'Change Password' }}
        </button>
      <button @click="handleDeleteAccount" class="danger">회원 탈퇴</button>
        <button @click="handleLogout" class="logout">Logout</button>
      </div>

      <div v-if="showUpdateForm" class="form-section">
        <h3>이름 수정</h3>
        <form @submit.prevent="handleUpdate">
          <div class="form-group">
            <label>이름</label>
            <input v-model="updateForm.name" type="text" required />
          </div>
          <button type="submit">저장</button>
          <p v-if="updateError" class="error">{{ updateError }}</p>
        </form>
      </div>

      <div v-if="showPasswordForm" class="form-section">
        <h3>비밀번호 변경</h3>
        <form @submit.prevent="handlePasswordChange">
          <div class="form-group">
            <label>현재 비밀번호</label>
            <div class="password-input-container">
              <input 
                v-model="passwordForm.oldPassword" 
                :type="showOldPassword ? 'text' : 'password'" 
                required 
              />
              <button 
                type="button" 
                class="password-toggle"
                @click="togglePasswordVisibility('oldPassword')"
                :title="showOldPassword ? '비밀번호 숨기기' : '비밀번호 보기'"
              >
                <span v-if="showOldPassword">👁️</span>
                <span v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label>새 비밀번호</label>
            <div class="password-input-container">
              <input 
                v-model="passwordForm.newPassword" 
                :type="showNewPassword ? 'text' : 'password'" 
                required 
              />
              <button 
                type="button" 
                class="password-toggle"
                @click="togglePasswordVisibility('newPassword')"
                :title="showNewPassword ? '비밀번호 숨기기' : '비밀번호 보기'"
              >
                <span v-if="showNewPassword">👁️</span>
                <span v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label>새 비밀번호 확인</label>
            <div class="password-input-container">
              <input 
                v-model="passwordForm.newPassword2" 
                :type="showNewPassword2 ? 'text' : 'password'" 
                required 
              />
              <button 
                type="button" 
                class="password-toggle"
                @click="togglePasswordVisibility('newPassword2')"
                :title="showNewPassword2 ? '비밀번호 숨기기' : '비밀번호 보기'"
              >
                <span v-if="showNewPassword2">👁️</span>
                <span v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>
          <button type="submit">비밀번호 변경</button>
          <p v-if="passwordError" class="error">{{ passwordError }}</p>
        </form>
      </div>
    </div>
    <div v-else>
      <p>Please <router-link to="/login">login</router-link> to view your profile.</p>
    </div>

  </div>
</template>

<script>
import AuthService from '@/services/AuthService';
import axios from 'axios';

export default {
  name: 'ProfileView',
  data() {
    return {
      user: null,
      showUpdateForm: false,
      showPasswordForm: false,
      showOldPassword: false,
      showNewPassword: false,
      showNewPassword2: false,
      updateForm: {
        name: ''
      },
      passwordForm: {
        oldPassword: '',
        newPassword: '',
        newPassword2: ''
      },
      updateError: '',
      passwordError: ''
    };
  },
  created() {
    this.loadUserProfile();
  },
  methods: {
    async loadUserProfile() {
      try {
        const response = await axios.get('http://localhost:8000/accounts/api/user/', {
          headers: AuthService.getAuthHeader()
        });
        this.user = response.data;
        this.updateForm.name = this.user.name || '';
      } catch (error) {
        console.error('Failed to load profile:', error);
        if (error.response?.status === 401) {
          this.$router.push('/login');
        }
      }
    },
    async handleUpdate() {
      try {
        await AuthService.updateProfile(this.updateForm);
        this.updateError = '';
        this.showUpdateForm = false;
        await this.loadUserProfile();
      } catch (error) {
        this.updateError = 'Failed to update profile. Please try again.';
        console.error('Update error:', error);
      }
    },
    async togglePasswordVisibility(field) {
      switch(field) {
        case 'oldPassword':
          this.showOldPassword = !this.showOldPassword;
          break;
        case 'newPassword':
          this.showNewPassword = !this.showNewPassword;
          break;
        case 'newPassword2':
          this.showNewPassword2 = !this.showNewPassword2;
          break;
      }
    },
    async handlePasswordChange() {
      // Clear previous errors
      this.passwordError = '';
      
      try {
        // Client-side validation
        if (this.passwordForm.newPassword !== this.passwordForm.newPassword2) {
          throw { response: { data: { new_password2: ['새 비밀번호가 일치하지 않습니다.'] } } };
        }
        
        if (this.passwordForm.oldPassword === this.passwordForm.newPassword) {
          throw { response: { data: { new_password: ['현재 비밀번호와 같습니다.'] } } };
        }
        
        await AuthService.changePassword(
          this.passwordForm.oldPassword,
          this.passwordForm.newPassword,
          this.passwordForm.newPassword2
        );
        
        // Reset form on success
        this.showPasswordForm = false;
        this.passwordForm = { oldPassword: '', newPassword: '', newPassword2: '' };
        
      } catch (error) {
        // Handle specific error cases
        if (error.response?.data?.old_password) {
          this.passwordError = error.response.data.old_password[0];
        } else if (error.response?.data?.new_password) {
          this.passwordError = error.response.data.new_password[0];
        } else if (error.response?.data?.new_password2) {
          this.passwordError = error.response.data.new_password2[0];
        } else {
          this.passwordError = error.response?.data?.detail || '비밀번호 변경에 실패했습니다.';
        }
      }
    },
    async handleDeleteAccount() {
      if (confirm('정말로 탈퇴하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
        try {
          await AuthService.deleteAccount();
          // Clear user data from local storage
          localStorage.removeItem('user');
          // Dispatch storage event to update auth state in Navbar
          window.dispatchEvent(new Event('storage'));
          // Redirect to home page
          this.$router.push('/');
        } catch (error) {
          console.error('회원 탈퇴 중 오류 발생:', error);
          alert('회원 탈퇴 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
      }
    },
    handleLogout() {
      AuthService.logout();
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
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
}

.password-toggle:hover {
  color: #333;
}

.profile-info {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.profile-actions {
  margin-bottom: 30px;
}

.profile-actions button {
  margin-right: 10px;
  margin-bottom: 10px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 5px;
  margin-top: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background: #4CAF50;
  color: white;
}

button.danger {
  background: #f44336;
}

button.logout {
  background: #2196F3;
}

.error {
  color: #f44336;
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
