import apiClient from '@/services/api';

// 예시 API 함수들 - 실제 프로젝트에 맞게 수정하세요
export const authAPI = {
  // 로그인
  login: (credentials) => apiClient.post('/accounts/login/', credentials),
  
  // 회원가입
  signup: (userData) => apiClient.post('/accounts/signup/', userData),
  
  // 로그아웃
  logout: () => apiClient.post('/accounts/logout/'),
  
  // 현재 사용자 정보 가져오기
  getCurrentUser: () => apiClient.get('/accounts/user/'),
};

export const productAPI = {
  // 제품 목록 가져오기
  getProducts: () => apiClient.get('/products/'),
  
  // 제품 상세 정보 가져오기
  getProduct: (id) => apiClient.get(`/products/${id}/`),
  
  // 제품 생성
  createProduct: (productData) => apiClient.post('/products/', productData),
  
  // 제품 수정
  updateProduct: (id, productData) => apiClient.put(`/products/${id}/`, productData),
  
  // 제품 삭제
  deleteProduct: (id) => apiClient.delete(`/products/${id}/`),
};

// 필요한 다른 API 함수들도 여기에 추가하세요
export default {
  auth: authAPI,
  product: productAPI,
};
