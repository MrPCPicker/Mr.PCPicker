// src/services/AuthService.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/accounts/api/';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

class AuthService {
  // Login user
  login(username, password) {
    console.log('Login attempt with:', { username, password }); // Debug log
    return axios
      .post(API_URL + 'token/', { username, password })
      .then(response => {
        if (response.data.access) {
          localStorage.setItem('user', JSON.stringify(response.data));
          // 🔹 로그인 성공 시 전역 auth 변경 이벤트
          window.dispatchEvent(new Event('auth-changed'));
        }
        return response.data;
      })
      .catch(error => {
        console.error('Login error:', error.response?.data); // Log detailed error
        throw error;
      });
  }
  
  // Logout user
  logout() {
    // 1. 먼저 클라이언트 상태를 정리
    const user = this.getCurrentUser();
    const headers =
      user && user.access
        ? { Authorization: 'Bearer ' + user.access }
        : {};

    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    window.dispatchEvent(new Event('auth-changed'));   // 🔴 NavBar 깨우기

    // 2. 백엔드에 알려주는 요청은 "옵션"으로, 실패해도 무시
    return axios
      .post(API_URL + 'logout/', null, { headers })
      .catch((error) => {
        console.warn('Logout API error (무시해도 됨):', error.response?.data || error.message);
      });
  }

  // Register new user
  register(name, username, password) {
    return axios.post(API_URL + 'register/', {
      name,
      username,
      password: password1,
      password2,
      email
    });
  }

  // Get current user
  getCurrentUser() {
    try {
      const raw = localStorage.getItem('user');
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      // 파싱 에러 나면 그냥 로그인 안 된 걸로 취급
      return null;
    }
  }

  // Update user profile
  updateProfile(userData) {
    return axios.put(API_URL + 'user/', userData, {
      headers: this.getAuthHeader()
    });
  }

  // Change password
  changePassword(oldPassword, newPassword, newPassword2) {
    return axios.post(
      API_URL + 'change-password/',
      { 
        old_password: oldPassword, 
        new_password: newPassword,
        new_password2: newPassword2
      },
      { 
        headers: this.getAuthHeader() 
      }
    );
  }

  // Delete account and logout
  async deleteAccount() {
    try {
      // First, make the delete request
      const response = await axios.delete(API_URL + 'user/delete/', {
        headers: this.getAuthHeader()
      });
      
      // Clear user data from local storage to log out
      localStorage.removeItem('user');
      
      // Clear any axios default headers
      delete axios.defaults.headers.common['Authorization'];

      // 🔹 회원 탈퇴 후 전역 auth 변경 이벤트
      window.dispatchEvent(new Event('auth-changed'));
      
      return response.data;
    } catch (error) {
      // If there's an error, still try to clear the local storage
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];

      // 🔹 에러가 나도 클라이언트 상태는 로그아웃된 것으로 동기화
      window.dispatchEvent(new Event('auth-changed'));
      
      // Re-throw the error so the calling component can handle it
      throw error;
    }
  }

  // Helper method to get auth header
  getAuthHeader() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user && user.access) {
      return { 'Authorization': 'Bearer ' + user.access };
    } else {
      return {};
    }
  }
  // Get user profile (프로필 조회)
  getProfile() {
    return api.get('user/', {
      headers: this.getAuthHeader(),
    })
  }

}

export default new AuthService();
