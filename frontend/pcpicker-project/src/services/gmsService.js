// src/services/gmsService.js
import axios from 'axios'

// ✅ Django REST API 서버 주소에 맞게 baseURL 조정
// 지금 프로젝트 urls.py 에서는 'api/' prefix 가 없으니까 그냥 루트로 맞춘다.
const gmsClient = axios.create({
  baseURL: 'http://localhost:8000',  // <-- /api 제거
  timeout: 30000,
})

export async function fetchLaptopRecommendations(query) {
  const response = await gmsClient.post('/gms/recommend-laptops/', {
    // SearchBar 에서 받은 니즈 텍스트
    query,
  })

  // 예상 응답 형식:
  // {
  //   results: [
  //     {
  //       id: 1,
  //       title: 'LG Gram 16 2024',
  //       price: 1890000,
  //       imageUrl: 'https://...',
  //       specs: ['CPU: ...', 'RAM: ...', ...]
  //     },
  //     ...
  //   ],
  //   needs: ['...', '...'],
  //   summary: '...',
  //   recommends: ['...', '...']
  // }
  return response.data
}
