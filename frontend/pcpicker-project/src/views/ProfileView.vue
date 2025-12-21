<template>
  <div class="profile-container">
    <h2 class="title">프로필 정보</h2>

    <div class="profile-card">
      <!-- 프로필 이미지 -->
      <div class="avatar" @click="triggerFileInput">
        <div class="profile-image-wrapper">
          <img 
            :src="user.profileImage || 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMjAiIGhlaWdodD0iMTIwIiB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzY2NiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMCAyMWMtMi43Ni0yLjQ4LTYuMzktNC03Ljk5LTUgLS4gMS0uMDItLjAzLS4wNS0uMDgtLjA5LS4xNi0uMTgtLjM4LS4zNy0uNjItLjU0LS4yNC0uMTctLjUyLS4zMS0uODItLjM4LS4zLS4wNy0uNjItLjA2LS45My4wMi0uMzEuMDgtLjYuMjYtLjg1LjUxLS4yNS4yNS0uNDMuNTQtLjUxLjg1LS4wOC4zMS0uMDkuNjMtLjAyLjkzLjA3LjMuMjEuNTguMzguODIuMTcuMjQuMzIuNDYuNDguNjIuMDYuMDcuMDguMDYuMDkuMDVsLjA1LjA4YzEuNiAxIDUuMjMgMi41MiA3Ljk5IDUgLjY3LjYyIDEuMDkgMS40NiAxLjE4IDIuMzguMDkuOTItLjE0IDEuODEtLjY3IDJhMS45OSAxLjk5IDAgMCAxLTEuNTEuNzZINGE0IDQgMCAwIDEtNC00YzAtLjcxLjE0LTEuMzkuNDItMnoiLz48Y2lyY2xlIGN4PSIxMiIgY3k9IjgiIHI9IjUiLz48L3N2Zz4='"
            alt="프로필 사진"
            class="profile-image"
          />
          <div class="edit-icon">✏️</div>
        </div>
        <input 
          type="file" 
          ref="fileInput" 
          @change="handleProfileImageChange" 
          accept="image/*" 
          style="display: none;"
        />
      </div>

      <!-- 프로필 정보 폼 -->
      <div class="profile-section">
        <h3 class="section-title">프로필 정보</h3>
        <form @submit.prevent="isEditing ? saveProfile() : startEditing()" class="profile-form">
          <div class="form-group">
            <label for="username">아이디</label>
            <input 
              id="username"
              type="text" 
              :value="user.username"
              disabled
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="name">이름</label>
            <input 
              id="name"
              type="text" 
              :value="isEditing ? editForm.name : user.name"
              @input="editForm.name = $event.target.value"
              :disabled="!isEditing"
              class="form-input"
              :class="{ 'editing': isEditing }"
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

          <div class="form-actions">
            <button 
              v-if="!isEditing"
              type="submit" 
              class="edit-btn"
            >
              수정하기
            </button>
            <template v-else>
              <button 
                type="button" 
                @click="cancelEditing" 
                class="cancel-btn"
              >
                취소
              </button>
              <button 
                type="submit" 
                class="save-btn"
                :disabled="isSaving"
              >
                {{ isSaving ? '저장 중...' : '저장하기' }}
              </button>
            </template>
          </div>

          <div class="password-change-container">
            <button 
              type="button" 
              @click="showPasswordForm = !showPasswordForm" 
              class="change-password-btn"
            >
              비밀번호 변경
            </button>
          </div>
        </form>
      </div>

      <!-- 비밀번호 변경 폼 -->
      <div v-if="showPasswordForm" class="password-section">
        <form @submit.prevent="handlePasswordChange" class="password-form">
          <div class="form-group">
            <label for="currentPassword">현재 비밀번호</label>
            <div class="password-input">
              <input 
                id="currentPassword"
                :type="showCurrentPassword ? 'text' : 'password'"
                v-model="passwordForm.currentPassword"
                class="form-input"
                required
              />
              <button 
                type="button" 
                class="toggle-password"
                @click="togglePasswordVisibility('current')"
              >
                <span v-if="showCurrentPassword">👁️</span>
                <span v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="newPassword">새 비밀번호</label>
            <div class="password-input">
              <input 
                id="newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                v-model="passwordForm.newPassword"
                class="form-input"
                required
              />
              <button 
                type="button" 
                class="toggle-password"
                @click="togglePasswordVisibility('new')"
              >
                <span v-if="showNewPassword">👁️</span>
                <span v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="confirmPassword">새 비밀번호 확인</label>
            <div class="password-input">
              <input 
                id="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                v-model="passwordForm.confirmPassword"
                class="form-input"
                required
              />
              <button 
                type="button" 
                class="toggle-password"
                @click="togglePasswordVisibility('confirm')"
              >
                <span v-if="showConfirmPassword">👁️</span>
                <span v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>

          <button type="submit" class="save-btn">
            비밀번호 변경
          </button>
        </form>
      </div>

      <!-- 기타 섹션들 -->
      <div class="cart-section">
        <h3 class="section-title">장바구니</h3>
        <div v-if="cartItems.length > 0" class="items-grid">
          <div v-for="(item, index) in cartItems" :key="'cart-' + index" class="item-card">
            <img :src="item.image" :alt="item.name" class="item-image">
            <div class="item-info">
              <h4>{{ item.name }}</h4>
              <p class="item-price">{{ formatPrice(item.price) }}원</p>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>장바구니가 비어있습니다.</p>
        </div>
      </div>

      <div class="recently-viewed-section">
        <h3 class="section-title">최근 본 상품</h3>
        <div v-if="recentlyViewedItems.length > 0" class="items-grid">
          <div v-for="(item, index) in recentlyViewedItems" :key="'recent-' + index" class="item-card">
            <img :src="item.image" :alt="item.name" class="item-image">
            <div class="item-info">
              <h4>{{ item.name }}</h4>
              <p class="item-price">{{ formatPrice(item.price) }}원</p>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>최근 본 상품이 없습니다.</p>
        </div>
      </div>

      <div class="action-buttons">
        <button class="logout-btn" @click="handleLogout">
          로그아웃
        </button>
        <button class="delete-account" @click="confirmDeleteAccount">
          회원 탈퇴
        </button>
      </div>
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
      showCurrentPassword: false,
      showNewPassword: false,
      showConfirmPassword: false,
      user: {
        profileImage: '',
        username: 'example_user',
        name: '홍길동',
        email: 'example@example.com'
      },
      editForm: {
        name: '',
        email: ''
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      cartItems: [
        { id: 1, name: '컴퓨터 부품 1', price: 150000, image: 'https://via.placeholder.com/80' },
        { id: 2, name: '컴퓨터 부품 2', price: 89000, image: 'https://via.placeholder.com/80' }
      ],
      recentlyViewedItems: [
        { id: 3, name: '최근 본 상품 1', price: 120000, image: 'https://via.placeholder.com/80' },
        { id: 4, name: '최근 본 상품 2', price: 75000, image: 'https://via.placeholder.com/80' },
        { id: 5, name: '최근 본 상품 3', price: 210000, image: 'https://via.placeholder.com/80' }
      ]
    };
  },
  created() {
    this.loadUserProfile();
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    handleProfileImageChange(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.user.profileImage = e.target.result;
          this.updateProfileImage(file);
        };
        reader.readAsDataURL(file);
      }
    },

    async updateProfileImage(file) {
      const formData = new FormData();
      formData.append('profile_image', file);
      
      try {
        await axios.patch(
          'http://localhost:8000/accounts/api/user/',
          formData,
          {
            headers: {
              ...AuthService.getAuthHeader(),
              'Content-Type': 'multipart/form-data'
            }
          }
        );
        alert('프로필 사진이 변경되었습니다.');
      } catch (error) {
        console.error('프로필 사진 변경 실패:', error);
        alert('프로필 사진 변경에 실패했습니다.');
      }
    },

    startEditing() {
      this.isEditing = true;
      this.editForm = {
        name: this.user.name || '',
        email: this.user.email || ''
      };
    },

    cancelEditing() {
      this.isEditing = false;
    },

    async saveProfile() {
      if (!this.editForm.name.trim()) {
        alert('이름을 입력해주세요.');
        return;
      }

      this.isSaving = true;
      try {
        await AuthService.updateProfile(this.editForm);
        this.user.name = this.editForm.name;
        this.user.email = this.editForm.email;
        this.isEditing = false;
        alert('프로필이 수정되었습니다.');
      } catch (error) {
        console.error('프로필 수정 실패:', error);
        alert('프로필 수정에 실패했습니다. 다시 시도해주세요.');
      } finally {
        this.isSaving = false;
      }
    },

    async loadUserProfile() {
      try {
        const response = await axios.get('http://localhost:8000/accounts/api/user/', {
          headers: AuthService.getAuthHeader()
        });
        this.user = response.data;
      } catch (error) {
        console.error('프로필 로드 실패:', error);
        if (error.response?.status === 401) {
          this.$router.push('/login');
        }
      }
    },

    togglePasswordVisibility(field) {
      this[`show${field.charAt(0).toUpperCase() + field.slice(1)}Password`] = 
        !this[`show${field.charAt(0).toUpperCase() + field.slice(1)}Password`];
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
        
        this.passwordForm = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        };
        this.showPasswordForm = false;
        alert('비밀번호가 성공적으로 변경되었습니다.');
      } catch (error) {
        console.error('비밀번호 변경 실패:', error);
        const errorMessage = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         '비밀번호 변경에 실패했습니다.';
        alert(errorMessage);
      }
    },

    handleLogout() {
      AuthService.logout();
      this.$router.push('/login');
    },

    confirmDeleteAccount() {
      if (confirm('정말로 회원 탈퇴하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
        this.deleteAccount();
      }
    },

    async deleteAccount() {
      try {
        await AuthService.deleteAccount();
        localStorage.removeItem('user');
        window.dispatchEvent(new Event('storage'));
        this.$router.push('/');
      } catch (error) {
        console.error('회원 탈퇴 실패:', error);
        alert('회원 탈퇴 중 오류가 발생했습니다. 다시 시도해주세요.');
      }
    },

    formatPrice(price) {
      return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.title {
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 30px;
  color: #333;
}

.profile-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

/* 프로필 이미지 스타일 */
.avatar {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 25px;
  cursor: pointer;
}

.profile-image-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #f0f0f0;
  transition: all 0.3s;
}

.profile-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background-color: #f5f5f5;
}

.edit-icon {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: white;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar:hover .edit-icon {
  opacity: 1;
}

.avatar:hover .profile-image {
  opacity: 0.8;
}

/* 폼 스타일 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s;
  background-color: #f9f9f9;
}

.form-input:disabled {
  background-color: #f0f0f0;
  color: #666;
}

.form-input.editing {
  background-color: #fff;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-input:focus {
  border-color: #4CAF50;
  background-color: white;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
  outline: none;
}

/* 버튼 스타일 */
.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.edit-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 12px 0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  width: 100%;
  transition: background-color 0.3s;
}

.edit-btn:hover {
  background-color: #45a049;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 12px 0;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  flex: 1;
  transition: background-color 0.3s;
}

.save-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.save-btn:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 12px 0;
  border-radius: 6px;
  font-size: 15px;
  cursor: pointer;
  flex: 1;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

/* 비밀번호 변경 버튼 */
.password-change-container {
  text-align: center;
  margin-top: 15px;
}

.change-password-btn {
  background: none;
  border: none;
  color: #2196F3;
  font-size: 13px;
  cursor: pointer;
  padding: 5px 0;
  text-decoration: underline;
  transition: color 0.2s;
}

.change-password-btn:hover {
  color: #0d8aee;
}

/* 비밀번호 입력 필드 */
.password-input {
  position: relative;
}

.password-input .form-input {
  padding-right: 40px;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 5px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;
}

/* 아이템 그리드 스타일 */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.item-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.item-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.item-image {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.item-info {
  padding: 12px;
}

.item-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-price {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2e7d32;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: #666;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 10px;
}

/* 섹션 간 간격 조정 */
.password-section,
.cart-section,
.recently-viewed-section {
  margin-top: 40px;
  padding-top: 25px;
  border-top: 1px solid #eee;
}

/* 액션 버튼 */
.action-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.logout-btn {
  padding: 10px 20px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background-color: #eee;
}

.delete-account {
  padding: 10px 20px;
  background-color: #fff;
  border: 1px solid #ff4d4f;
  border-radius: 6px;
  color: #ff4d4f;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-account:hover {
  background-color: #fff2f0;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .items-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .profile-card {
    padding: 20px;
  }
  
  .items-grid {
    grid-template-columns: 1fr;
  }
  
  .section-title {
    font-size: 16px;
  }
}
</style>