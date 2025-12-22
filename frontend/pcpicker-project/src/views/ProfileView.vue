<template>
  <div class="profile-container">
    <h2 class="title">프로필 정보</h2>

    <div class="profile-card">
      <div class="avatar-container">
        <div class="avatar" @click="triggerFileInput">
          <img 
            :src="user.profile_image || 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMjAiIGhlaWdodD0iMTIwIiB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzY2NiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMCAyMWMtMi43Ni0yLjQ4LTYuMzktNC03Ljk5LTUgLS4gMS0uMDItLjAzLS4wNS0uMDgtLjA5LS4xNi0uMTgtLjM4LS4zNy0uNjItLjU0LS4yNC0uMTctLjUyLS4zMS0uODItLjM4LS4zLS4wNy0uNjItLjA2LS45My4wMi0uMzEuMDgtLjYuMjYtLjg1LjUxLS4yNS4yNS0uNDMuNTQtLjUxLjg1LS4wOC4zMS0uMDkuNjMtLjAyLjkzLjA3LjMuMjEuNTguMzguODIuMTcuMjQuMzIuNDYuNDguNjIuMDYuMDcsLjA4LjA2LjA5LjA1bC4wNS4wOGMxLjYgMSA1LjIzIDIuNTIgNy45OSIDUgLjY3LjYyIDEuMDkgMS40NiAxLjE4IDIuMzguMDkuOTItLjE0IDEuODEtLjY3IDJhMS45OSAxLjk5IDAgMCAxLTEuNTEuNzZINGE0IDQgMCAwIDEtNC00YzAtLjcxLjE0LTEuMzkuNDItMXoiLz48Y2lyY2xlIGN4PSIxMiIgY3k9IjgiIHI9IjUiLz48L3N2Zz4='"
            alt="프로필 사진"
            class="profile-image"
            :key="user.profile_image"
          />
        </div>
        <div class="edit-icon" @click="triggerFileInput">
          <span>✏️</span>
        </div>
        <input 
          type="file" 
          ref="fileInput" 
          @change="handleProfileImageChange" 
          accept="image/*" 
          style="display: none;"
        />
      </div>

      <div class="profile-section">
        <h3 class="section-title">회원 정보</h3>
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
            <button v-if="!isEditing" type="submit" class="edit-btn">수정하기</button>
            <template v-else>
              <button type="button" @click="cancelEditing" class="cancel-btn">취소</button>
              <button type="submit" class="save-btn" :disabled="isSaving">
                {{ isSaving ? '저장 중...' : '저장하기' }}
              </button>
            </template>
          </div>

          <div class="password-change-container">
            <button type="button" @click="showPasswordForm = !showPasswordForm" class="change-password-btn">
              비밀번호 변경
            </button>
          </div>
        </form>
      </div>

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
              <button type="button" class="toggle-password" @click="togglePasswordVisibility('current')">
                <span v-if="showCurrentPassword">👁️</span>
                <span v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label for="newPassword">새 비밀번호</label>
            <div class="password-input">
              <input id="newPassword" :type="showNewPassword ? 'text' : 'password'" v-model="passwordForm.newPassword" class="form-input" required />
              <button type="button" class="toggle-password" @click="togglePasswordVisibility('new')">
                <span v-if="showNewPassword">👁️</span>
                <span v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label for="confirmPassword">새 비밀번호 확인</label>
            <div class="password-input">
              <input id="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" v-model="passwordForm.confirmPassword" class="form-input" required />
              <button type="button" class="toggle-password" @click="togglePasswordVisibility('confirm')">
                <span v-if="showConfirmPassword">👁️</span>
                <span v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>
          <button type="submit" class="save-btn">비밀번호 변경</button>
        </form>
      </div>

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
        <div v-else class="empty-state"><p>장바구니가 비어있습니다.</p></div>
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
        <div v-else class="empty-state"><p>최근 본 상품이 없습니다.</p></div>
      </div>

      <div class="action-buttons">
        <button class="logout-btn" @click="handleLogout">로그아웃</button>
        <button class="delete-account" @click="confirmDeleteAccount">회원 탈퇴</button>
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
      user: { profile_image: '', username: '', email: '' },
      editForm: { email: '' },
      passwordForm: { currentPassword: '', newPassword: '', confirmPassword: '' },
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
    triggerFileInput() { this.$refs.fileInput.click(); },
    handleProfileImageChange(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.user.profile_image = e.target.result;
          this.updateProfileImage(file);
        };
        reader.readAsDataURL(file);
      }
    },
    async updateProfileImage(file) {
      const formData = new FormData();
      formData.append('profile_image', file);
      try {
        await axios.put('http://localhost:8000/accounts/api/user/', formData, {
          headers: { ...AuthService.getAuthHeader(), 'Content-Type': 'multipart/form-data' }
        });
        alert('프로필 사진이 변경되었습니다.');
        this.loadUserProfile();
      } catch (error) { alert('사진 변경 실패'); }
    },
    startEditing() {
      this.isEditing = true;
      this.editForm.email = this.user.email || '';
    },
    cancelEditing() { this.isEditing = false; },
    async saveProfile() {
      // [요청 사항] 이메일 비어있을 시 경고
      if (!this.editForm.email || !this.editForm.email.trim()) {
        alert('이메일을 다시 입력해주세요.');
        return;
      }
      this.isSaving = true;
      try {
        await AuthService.updateProfile({ email: this.editForm.email });
        this.user.email = this.editForm.email;
        this.isEditing = false;
        alert('프로필이 수정되었습니다.');
      } catch (error) { alert('이메일을 올바른 양식으로 입력해주세요.'); }
      finally { this.isSaving = false; }
    },
    async loadUserProfile() {
      try {
        const response = await axios.get('http://localhost:8000/accounts/api/user/', {
          headers: AuthService.getAuthHeader()
        });
        this.user = response.data;
      } catch (error) {
        if (error.response?.status === 401) this.$router.push('/login');
      }
    },
    togglePasswordVisibility(field) {
      const key = `show${field.charAt(0).toUpperCase() + field.slice(1)}Password`;
      this[key] = !this[key];
    },
    async handlePasswordChange() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        alert('새 비밀번호가 일치하지 않습니다.');
        return;
      }
      try {
        await AuthService.changePassword(this.passwordForm.currentPassword, this.passwordForm.newPassword, this.passwordForm.confirmPassword);
        alert('비밀번호가 변경되었습니다.');
        this.showPasswordForm = false;
        this.passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };
      } catch (error) { alert(error.response?.data?.detail || '변경 실패'); }
    },
    handleLogout() { AuthService.logout(); this.$router.push('/login'); },
    confirmDeleteAccount() { if (confirm('정말로 회원 탈퇴하시겠습니까?')) this.deleteAccount(); },
    async deleteAccount() {
      try {
        await AuthService.deleteAccount();
        localStorage.removeItem('user');
        this.$router.push('/');
      } catch (error) { alert('탈퇴 실패'); }
    },
    formatPrice(price) { return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  }
};
</script>

<style scoped>
/* 기존 디자인 코드 유지 */
.profile-container { max-width: 800px; margin: 0 auto; padding: 20px; }
.title { text-align: center; font-size: 24px; font-weight: 600; margin-bottom: 30px; color: #333; }
.profile-card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); }
.avatar-container { position: relative; width: 120px; height: 120px; margin: 0 auto 25px; }
.avatar { width: 100%; height: 100%; border-radius: 50%; overflow: hidden; border: 3px solid #f0f0f0; cursor: pointer; transition: all 0.3s; }
.avatar:hover { opacity: 0.9; }
.profile-image { width: 100%; height: 100%; object-fit: cover; background-color: #f5f5f5; }
.edit-icon { position: absolute; bottom: 5px; right: 5px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.2); width: 30px; height: 30px; cursor: pointer; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-size: 14px; color: #555; font-weight: 500; }
.form-input { width: 100%; padding: 12px 15px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; background-color: #f9f9f9; transition: all 0.3s; }
.form-input:disabled { background-color: #f0f0f0; color: #666; }
.form-input.editing { background-color: #fff; border-color: #4CAF50; box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2); }
.form-actions { display: flex; gap: 10px; margin-top: 20px; }
.edit-btn { background-color: #4CAF50; color: white; border: none; padding: 12px 0; border-radius: 6px; cursor: pointer; font-size: 15px; width: 100%; }
.save-btn { background-color: #4CAF50; color: white; border: none; padding: 12px 0; border-radius: 6px; font-size: 15px; cursor: pointer; flex: 1; }
.save-btn:disabled { background-color: #a5d6a7; cursor: not-allowed; }
.cancel-btn { background-color: #f5f5f5; border: 1px solid #ddd; padding: 12px 0; border-radius: 6px; font-size: 15px; cursor: pointer; flex: 1; }
.password-change-container { text-align: center; margin-top: 15px; }
.change-password-btn { background: none; border: none; color: #2196F3; font-size: 13px; cursor: pointer; text-decoration: underline; }
.password-input { position: relative; }
.toggle-password { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #666; cursor: pointer; }
.items-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; margin-top: 15px; }
.item-card { border: 1px solid #eee; border-radius: 8px; overflow: hidden; transition: transform 0.2s; }
.item-card:hover { transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.item-image { width: 100%; height: 120px; object-fit: cover; }
.item-info { padding: 12px; }
.item-info h4 { margin: 0 0 8px 0; font-size: 14px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-price { margin: 0; font-size: 16px; font-weight: 600; color: #2e7d32; }
.empty-state { text-align: center; padding: 30px; color: #666; background-color: #f9f9f9; border-radius: 8px; margin-top: 10px; }
.password-section, .cart-section, .recently-viewed-section { margin-top: 40px; padding-top: 25px; border-top: 1px solid #eee; }
.action-buttons { display: flex; justify-content: space-between; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
.logout-btn { padding: 10px 20px; background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 6px; color: #333; cursor: pointer; }
.delete-account { padding: 10px 20px; background-color: #fff; border: 1px solid #ff4d4f; border-radius: 6px; color: #ff4d4f; cursor: pointer; }
</style>