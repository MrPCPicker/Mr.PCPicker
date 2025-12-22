// src/services/AuthService.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/accounts/api/';

// axios 인스턴스 (프로필 조회 등에 사용)
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

class AuthService {
  // 🔐 Login
  login(username, password) {
    console.log('Login attempt with:', { username, password });
    return axios
      .post(API_URL + 'token/', { username, password })
      .then((response) => {
        if (response.data.access) {
          // 토큰 + 유저 정보 저장
          localStorage.setItem('user', JSON.stringify(response.data));
          // 전역 auth 변경 이벤트
          window.dispatchEvent(new Event('auth-changed'));
          // axios 기본 헤더 세팅 (선택)
          axios.defaults.headers.common['Authorization'] =
            'Bearer ' + response.data.access;
        }
        return response.data;
      })
      .catch((error) => {
        console.error('Login error:', error.response?.data || error.message);
        throw error;
      });
  }

  // 🚪 Logout
  logout() {
    const user = this.getCurrentUser();
    const headers =
      user && user.access
        ? { Authorization: 'Bearer ' + user.access }
        : {};

    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    window.dispatchEvent(new Event('auth-changed'));

    return axios
      .post(API_URL + 'logout/', null, { headers })
      .catch((error) => {
        console.warn(
          'Logout API error (무시해도 됨):',
          error.response?.data || error.message,
        );
      });
  }

  /**
   * 🧾 Register new user
   *
   * - 모달에서: AuthService.register(formData)
   *   -> { name, username, email, password, password2 }
   * - 예전 방식: AuthService.register(name, username, password)
   */
  register(nameOrData, username, password) {
    let payload = {};

    if (typeof nameOrData === 'object' && nameOrData !== null) {
      // ✅ formData 객체 버전
      const data = nameOrData;
      payload = {
        name: data.name,
        username: data.username,
        email: data.email,
        password: data.password,
        password2: data.password2 ?? data.password,
      };
    } else {
      // ✅ 옛 방식(파라미터 3개) 호환
      payload = {
        name: nameOrData,
        username,
        password,
        password2: password,
      };
    }

    return axios.post(API_URL + 'register/', payload).then((response) => {
      const data = response.data;

      // 백엔드 응답 예시:
      // { message, user: {...}, tokens: { access, refresh } }
      if (data.tokens && data.tokens.access) {
        const storedUser = {
          access: data.tokens.access,
          refresh: data.tokens.refresh,
          user: data.user,
        };

        localStorage.setItem('user', JSON.stringify(storedUser));
        axios.defaults.headers.common['Authorization'] =
          'Bearer ' + data.tokens.access;
        window.dispatchEvent(new Event('auth-changed'));
      }

      return data;
    });
  }

  // 현재 user 가져오기
  getCurrentUser() {
    try {
      const raw = localStorage.getItem('user');
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  // 프로필 업데이트
  updateProfile(userData) {
    return axios.put(API_URL + 'user/', userData, {
      headers: this.getAuthHeader(),
    });
  }

  // 비밀번호 변경
  changePassword(oldPassword, newPassword, newPassword2) {
    return axios.post(
      API_URL + 'change-password/',
      {
        old_password: oldPassword,
        new_password: newPassword,
        new_password2: newPassword2,
      },
      {
        headers: this.getAuthHeader(),
      },
    );
  }

  // 회원 탈퇴
  async deleteAccount() {
    try {
      const response = await axios.delete(API_URL + 'user/delete/', {
        headers: this.getAuthHeader(),
      });

      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
      window.dispatchEvent(new Event('auth-changed'));

      return response.data;
    } catch (error) {
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
      window.dispatchEvent(new Event('auth-changed'));
      throw error;
    }
  }

  // Authorization 헤더 생성
  getAuthHeader() {
    const raw = localStorage.getItem('user');
    const user = raw ? JSON.parse(raw) : null;
    if (user && user.access) {
      return { Authorization: 'Bearer ' + user.access };
    }
    return {};
  }

  // 프로필 조회
  getProfile() {
    return api.get('user/', {
      headers: this.getAuthHeader(),
    });
  }
}

export default new AuthService();
