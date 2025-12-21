// src/services/gmsService.js
import axios from 'axios'

// ✅ Django REST API 서버 주소에 맞게 baseURL 조정
// 지금 프로젝트 urls.py 에서는 'api/' prefix 가 없으니까 그냥 루트로 맞춘다.
const gmsClient = axios.create({
  baseURL: 'http://localhost:8000',  // <-- /api 제거
  timeout: 30000,
})

let isLoading = false

export async function fetchLaptopRecommendations(query) {
  if (isLoading) {
    console.warn('GMS 요청 중복 차단')
    return null
  }

  isLoading = true
  try {
    const response = await gmsClient.post('/gms/recommend-laptops/', {
      // SearchBar 에서 받은 니즈 텍스트
      query,
    })
    return response.data
  } finally {
    isLoading = false
  }
}
