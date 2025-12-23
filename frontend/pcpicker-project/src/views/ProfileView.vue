<template>
  <div class="profile-page">
    <div class="profile-container">
      <header class="profile-header">
        <h2 class="title">My Profile</h2>
        <p class="subtitle">계정 설정 및 프로필 정보를 관리할 수 있습니다.</p>
      </header>

      <section class="profile-card">
        <h3 class="section-title">기본 정보</h3>
        <form @submit.prevent="isEditing ? saveProfile() : startEditing()" class="profile-form">
          
          <div class="form-group">
            <label for="username">아이디 (변경 불가)</label>
            <input 
              id="username"
              type="text" 
              :value="user.username"
              disabled
              class="form-input disabled"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="name">이름</label>
              <input 
                id="name"
                type="text" 
                :value="isEditing ? editForm.name : (user.name || '')"
                @input="editForm.name = $event.target.value"
                :disabled="!isEditing"
                class="form-input"
                :class="{ 'editing': isEditing }"
                placeholder="이름을 입력하세요"
              />
            </div>

            <div class="form-group">
              <label for="email">이메일</label>
              <input 
                id="email"
                type="email" 
                :value="isEditing ? editForm.email : (user.email || '')"
                @input="editForm.email = $event.target.value"
                :disabled="!isEditing"
                class="form-input"
                :class="{ 'editing': isEditing }"
                placeholder="이메일을 입력하세요"
              />
            </div>
          </div>

          <div class="form-actions">
            <button v-if="!isEditing" type="submit" class="edit-btn">프로필 수정하기</button>
            <template v-else>
              <button type="button" @click="cancelEditing" class="cancel-btn">취소</button>
              <button type="submit" class="save-btn" :disabled="isSaving">
                {{ isSaving ? '저장 중...' : '변경 사항 저장' }}
              </button>
            </template>
          </div>

          <div class="password-toggle-area">
            <button type="button" @click="showPasswordForm = !showPasswordForm" class="change-password-btn">
              {{ showPasswordForm ? '비밀번호 변경 닫기' : '비밀번호 변경하기' }}
            </button>
          </div>
        </form>

        <transition name="fade">
          <div v-if="showPasswordForm" class="password-form-wrapper">
            <form @submit.prevent="handlePasswordChange" class="password-form">
              <div class="form-group">
                <label>현재 비밀번호</label>
                <input type="password" v-model="passwordForm.currentPassword" class="form-input" required />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>새 비밀번호</label>
                  <input type="password" v-model="passwordForm.newPassword" class="form-input" required />
                </div>
                <div class="form-group">
                  <label>새 비밀번호 확인</label>
                  <input type="password" v-model="passwordForm.confirmPassword" class="form-input" required />
                </div>
              </div>
              <button type="submit" class="save-btn secondary">비밀번호 업데이트</button>
            </form>
          </div>
        </transition>
      </section>

      <footer class="profile-footer">
        <button class="logout-link" @click="handleLogout">로그아웃</button>
        <div class="divider"></div>
        <button class="delete-link" @click="confirmDeleteAccount">회원 탈퇴</button>
      </footer>
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
      isEditing: false,
      isSaving: false,
      showPasswordForm: false,
      user: { username: '', email: '', name: '' },
      editForm: { email: '', name: '' },
      passwordForm: { currentPassword: '', newPassword: '', confirmPassword: '' },
    };
  },
  created() {
    this.loadUserProfile();
  },
  methods: {
    startEditing() {
      this.isEditing = true;
      this.editForm = {
        email: this.user.email || '',
        name: this.user.name || ''
      };
    },
    cancelEditing() { this.isEditing = false; },
    async saveProfile() {
      this.isSaving = true;
      try {
        const response = await AuthService.updateProfile({ 
          email: this.editForm.email,
          name: this.editForm.name 
        });
        
        if (response.data) {
          this.user = {
            ...this.user,
            email: response.data.email || this.editForm.email,
            name: response.data.name || this.editForm.name,
          };
        }
        
        // 로컬 스토리지 갱신 및 Navbar 동기화
        const storedUser = AuthService.getCurrentUser();
        if (storedUser && storedUser.user) {
          storedUser.user = { ...storedUser.user, email: this.user.email, name: this.user.name };
          localStorage.setItem('user', JSON.stringify(storedUser));
        }
        window.dispatchEvent(new Event('auth-changed'));
        
        this.isEditing = false;
        alert('프로필이 성공적으로 수정되었습니다.');
      } catch (error) { 
        alert('업데이트 중 오류가 발생했습니다.');
      } finally { 
        this.isSaving = false; 
      }
    },
    async loadUserProfile() {
      try {
        const response = await axios.get('http://localhost:8000/accounts/api/user/', {
          headers: AuthService.getAuthHeader()
        });
        this.user = { ...this.user, ...response.data };
        this.editForm.email = response.data.email || '';
        this.editForm.name = response.data.name || '';
      } catch (error) {
        if (error.response?.status === 401) this.$router.push('/');
      }
    },
    async handlePasswordChange() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        alert('새 비밀번호가 일치하지 않습니다.');
        return;
      }
      try {
        await AuthService.changePassword(
          this.passwordForm.currentPassword, 
          this.passwordForm.newPassword, 
          this.passwordForm.confirmPassword
        );
        alert('비밀번호가 변경되었습니다.');
        this.showPasswordForm = false;
        this.passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };
      } catch (error) { 
        alert(error.response?.data?.detail || '변경 실패'); 
      }
    },
    handleLogout() { 
      AuthService.logout(); 
      window.dispatchEvent(new Event('auth-changed'));
      this.$router.push('/');
    },
    confirmDeleteAccount() { 
      if (confirm('정말로 회원 탈퇴하시겠습니까?')) this.deleteAccount(); 
    },
    async deleteAccount() {
      try {
        await AuthService.deleteAccount();
        AuthService.logout();
        window.dispatchEvent(new Event('auth-changed'));
        this.$router.push('/');
      } catch (error) { 
        alert('탈퇴 실패'); 
      }
    }
  }
};
</script>

<style scoped>
.profile-page {
  background-color: #f8f9fa;
  min-height: 100vh;
  padding: 80px 20px;
  font-family: system-ui, -apple-system, sans-serif;
}

.profile-container {
  max-width: 700px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: 40px;
  text-align: left;
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: #2f3a45;
  margin-bottom: 8px;
}

.subtitle {
  color: #6c757d;
  font-size: 16px;
}

.profile-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  margin-bottom: 40px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #2f3a45;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 15px;
  color: #212529;
  box-sizing: border-box;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #2f3a45;
}

.form-input.disabled {
  background-color: #f8f9fa;
  color: #adb5bd;
  cursor: not-allowed;
}

.form-input.editing {
  border-color: #1e6fd7;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}

.edit-btn, .save-btn {
  padding: 14px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-size: 15px;
}

.edit-btn {
  background-color: #2f3a45;
  color: white;
  width: 100%;
}

.save-btn {
  background-color: #1e6fd7;
  color: white;
  flex: 1;
}

.save-btn.secondary {
  width: 100%;
  margin-top: 10px;
}

.cancel-btn {
  padding: 14px;
  background-color: #f1f3f5;
  border-radius: 8px;
  color: #495057;
  border: none;
  cursor: pointer;
  flex: 1;
}

.password-toggle-area {
  margin-top: 24px;
  text-align: center;
}

.change-password-btn {
  background: none;
  border: none;
  color: #1e6fd7;
  font-weight: 500;
  cursor: pointer;
  text-decoration: underline;
  font-size: 14px;
}

.password-form-wrapper {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px dashed #dee2e6;
}

.profile-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.logout-link, .delete-link {
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  color: #868e96;
}

.delete-link:hover {
  color: #fa5252;
  text-decoration: underline;
}

.divider {
  width: 1px;
  height: 14px;
  background-color: #dee2e6;
}

/* 애니메이션 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>