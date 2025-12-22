// src/services/gmsService.js
import axios from 'axios'

// --------------------
// 🔧 설정: 여기만 바꿔서 GMS ON/OFF
// --------------------
const USE_MOCK = true   // ✅ 프론트만 작업할 땐 true
// const USE_MOCK = false  // ✅ 실제 GMS 쓰고 싶을 땐 이걸로 교체

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
      title: 'Mock Laptop 1 (학생용 워드/과제)',
      price: 799000,
      imageUrl: '',
      specs: [
        'CPU: Intel Core i5-1240P',
        'RAM: 16GB',
        'Storage: 512GB SSD',
        'GPU: 내장 그래픽',
      ],
    },
    {
      id: 2,
      title: 'Mock Laptop 2 (휴대성 좋은 노트북)',
      price: 999000,
      imageUrl: '',
      specs: [
        'CPU: AMD Ryzen 5',
        'RAM: 16GB',
        'Storage: 512GB SSD',
        'GPU: 내장 그래픽',
      ],
    },
    {
      id: 3,
      title: 'Mock Laptop 3 (가성비 기본형)',
      price: 649000,
      imageUrl: '',
      specs: [
        'CPU: Intel Core i3',
        'RAM: 8GB',
        'Storage: 256GB SSD',
        'GPU: 내장 그래픽',
      ],
    },
  ],
  needs: [
    '대학생, 워드/과제/온라인 강의 위주 사용',
    '휴대성은 어느 정도 중요하지만, 게이밍은 필수 아님',
  ],
  recommends: [
    'RAM 16GB 이상',
    'SSD 256GB 이상',
    '내장 그래픽만으로도 충분',
  ],
}

// --------------------
// 🔹 실제로 프론트에서 호출하는 함수
// --------------------
export async function fetchLaptopRecommendations(query) {
  if (USE_MOCK) {
    console.log('[MOCK] fetchLaptopRecommendations called with:', query)

    // 약간의 딜레이를 줘서 실제처럼 보이게 (선택 사항)
    await new Promise((resolve) => setTimeout(resolve, 500))

    return mockResponse
  }

  // 🔻 실제 GMS 사용하는 경로 (나중에 다시 켤 때 사용)
  const response = await gmsClient.post('/gms/recommend-laptops/', {
    query,
  })
  return response.data
}
