import axios from 'axios';

// API 기본 URL 설정 - Django 백엔드 서버 주소로 설정
const API_URL = 'http://localhost:8000';

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // 쿠키를 포함한 요청을 보내기 위해 필요
});

// 요청 인터셉터 (요청 전에 실행됨)
apiClient.interceptors.request.use(
  (config) => {
    // 로컬 스토리지에서 토큰 가져오기
    const token = localStorage.getItem('access');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// API 함수들
export const auth = {
  register: (userData) => apiClient.post('/accounts/api/register/', userData),
  login: (credentials) => apiClient.post('/accounts/api/token/', credentials),
  refreshToken: (refresh) => apiClient.post('/accounts/api/token/refresh/', { refresh }),
  getProfile: () => apiClient.get('/accounts/api/user/'),
  updateProfile: (userData) => apiClient.put('/accounts/api/user/', userData),
  changePassword: (passwords) => apiClient.post('/accounts/api/change-password/', passwords),
  deleteAccount: () => apiClient.delete('/accounts/api/user/delete/')
};

// 응답 인터셉터 (응답을 받은 후 실행됨)
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // 401 에러가 발생하고, 토큰 갱신이 아직 시도되지 않은 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // 리프레시 토큰으로 액세스 토큰 갱신 시도
        const refreshToken = localStorage.getItem('refresh');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/accounts/token/refresh/`, {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          localStorage.setItem('access', access);
          
          // 원래 요청을 새로운 액세스 토큰으로 재시도
          originalRequest.headers['Authorization'] = `Bearer ${access}`;
          return apiClient(originalRequest);
        }
      } catch (error) {
        // 토큰 갱신 실패 시 로그인 페이지로 리다이렉트
        console.error('토큰 갱신 실패:', error);
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
