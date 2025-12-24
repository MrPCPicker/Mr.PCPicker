// src/services/gmsService.js
import axios from 'axios'

// --------------------
// 🔧 설정: 여기만 바꿔서 GMS ON/OFF
// --------------------
const USE_MOCK = true   // ✅ 실제 GMS를 사용하려면 이 값을 false로 설정 (현재는 개발을 위해 Mock 데이터 사용 중)

// ✅ Django REST API 서버 주소
const gmsClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
})

// --------------------
// 🔹 목 데이터 (프론트 UI 개발용)
// --------------------
const mockResponse = {
  results: [
    {
      id: 1,
      title: 'Mock Computer 1',
      price: 799000,
      imageUrl: '',
      specs: ['CPU: Intel Core i5', 'RAM: 16GB', 'Storage: 512GB SSD'],
    },
    {
      id: 2,
      title: 'Mock Computer 2',
      price: 999000,
      imageUrl: '',
      specs: ['CPU: AMD Ryzen 5', 'RAM: 16GB', 'Storage: 512GB SSD'],
    },
    {
      id: 3,
      title: 'Mock Computer 3',
      price: 649000,
      imageUrl: '',
      specs: ['CPU: Intel Core i3', 'RAM: 8GB', 'Storage: 256GB SSD'],
    },
  ],
  needs: ['문서/웹 서핑 위주', '가성비 중시'],
  recommends: ['RAM 16GB 이상', 'SSD 256GB 이상'],
}

export async function fetchComputerRecommendations(query) {
  if (USE_MOCK) {
    console.log('[MOCK] fetchComputerRecommendations called with:', query)

    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockResponse
  }

  const response = await gmsClient.post('/gms/recommend-computers/', {
    query,
  })
  return response.data
}

export const fetchLaptopRecommendations = fetchComputerRecommendations
