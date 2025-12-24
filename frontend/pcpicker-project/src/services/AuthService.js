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

// 요청 인터셉터 - 토큰 자동 주입
api.interceptors.request.use(
  (config) => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user?.access) {
      config.headers.Authorization = `Bearer ${user.access}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 토큰 만료 시 자동 갱신
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // 401 에러이고, 이미 재시도한 요청이 아닌 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (user?.refresh) {
          // 토큰 갱신 시도
          const response = await axios.post(`${API_URL}token/refresh/`, {
            refresh: user.refresh
          });
          
          const { access } = response.data;
          
          // 새 토큰 저장
          const updatedUser = { ...user, access };
          localStorage.setItem('user', JSON.stringify(updatedUser));
          
          // 원래 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        console.error('토큰 갱신 실패:', refreshError);
        // 토큰 갱신 실패 시 로그아웃 처리
        localStorage.removeItem('user');
        delete axios.defaults.headers.common['Authorization'];
        window.dispatchEvent(new Event('auth-changed'));
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

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

  // 토큰 갱신
  async refreshToken() {
    try {
      const user = this.getCurrentUser();
      if (!user?.refresh) {
        throw new Error('No refresh token available');
      }

      const response = await axios.post(`${API_URL}token/refresh/`, {
        refresh: user.refresh
      });

      if (response.data.access) {
        // 새 액세스 토큰으로 사용자 정보 업데이트
        const updatedUser = { ...user, access: response.data.access };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        
        // axios 기본 헤더 업데이트
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
        
        // 인증 상태 변경 이벤트 발생
        window.dispatchEvent(new Event('auth-changed'));
        
        return response.data.access;
      }
    } catch (error) {
      console.error('토큰 갱신 실패:', error);
      this.logout();
      throw error;
    }
  }

  // Authorization 헤더 생성
  getAuthHeader() {
    const user = this.getCurrentUser();
    if (user?.access) {
      return { 
        'Authorization': `Bearer ${user.access}`,
        'Content-Type': 'application/json'
      };
    }
    return {};
  }

  // 프로필 조회
  async getProfile() {
    try {
      const response = await api.get('user/');
      return response;
    } catch (error) {
      if (error.response?.status === 401) {
        try {
          await this.refreshToken();
          const retryResponse = await api.get('user/');
          return retryResponse;
        } catch (refreshError) {
          this.logout();
          throw new Error('세션이 만료되었습니다. 다시 로그인해주세요.');
        }
      }
      throw error;
    }
  }
}

export default new AuthService();
