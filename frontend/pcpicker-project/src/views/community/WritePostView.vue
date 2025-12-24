<template>
  <div class="write-container">
    <div class="write-header">
      <h1>새 게시글 작성</h1>
      <p>Mr.PCpicker 커뮤니티 페이지입니다. 자유롭게 의견을 나눠주세요.</p>
    </div>

    <form class="write-form" @submit.prevent="submitPost">
      <div class="form-group">
        <label for="category">카테고리</label>
        <div class="select-wrapper">
          <select id="category" v-model="category">
            <option value="NOTICE">공지사항</option>
            <option value="QNA">Q&A</option>
            <option value="ESTIMATE">견적질문</option>
            <option value="FREE">자유게시판</option>
          </select>
        </div>
      </div>

      <div v-if="category === 'ESTIMATE'" class="form-group">
        <label for="laptop">노트북 선택 <span class="required">*</span></label>
        <p class="help-text">찜 목록에 있는 노트북 중 하나를 선택해주세요.</p>
        <div class="select-wrapper">
          <select id="laptop" v-model="selectedLaptopId" required>
            <option value="" disabled selected>-- 노트북을 선택해주세요 --</option>
            <option 
              v-for="laptop in wishlist" 
              :key="laptop.id" 
              :value="laptop.id"
            >
              {{ laptop.name }} ({{ formatPrice(laptop.price) }}원)
            </option>
          </select>
        </div>
        <p v-if="wishlist.length === 0" class="error-text">
          <i class="fas fa-exclamation-circle"></i> 찜 목록에 노트북이 없습니다. 먼저 상품을 찜해주세요.
        </p>
      </div>
      
      <div v-if="category === 'ESTIMATE'" class="form-group estimate-note">
        <div class="info-box">
          <i class="fas fa-lightbulb"></i>
          <div>
            <strong>견적에 대한 질문을 작성해주세요😁</strong>
            <p>예시:</p>
            <ul>
              <li>이 정도면 가격이 괜찮은 편인가요?</li>
              <li>이 사양으로 영상 편집이 가능할까요?</li>
              <li>배터리 수명이 궁금해요.</li>
              <li>이 가격대에 다른 추천 모델이 있을까요?</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="title">제목</label>
        <input
          id="title"
          v-model="title"
          type="text"
          placeholder="제목을 입력하세요"
          required
        />
      </div>

      <div class="form-group">
        <label for="content">내용 <span class="required">*</span></label>
        <p v-if="category === 'ESTIMATE'" class="help-text">
          견적에 대한 구체적인 질문을 작성해주세요. 다른 사용자들이 도움을 드릴 수 있도록 자세히 적어주시면 좋아요!
        </p>
        <textarea
          id="content"
          v-model="content"
          :placeholder="category === 'ESTIMATE' ? '예) 이 노트북으로 4K 영상 편집이 가능할까요?\n\n- 사용 목적: 유튜브 4K 영상 편집\n- 주로 사용하는 프로그램: Adobe Premiere Pro, After Effects\n- 기타 고려사항: 배터리 수명도 궁금합니다.' : '내용을 작성해 주세요.'"
          rows="12"
          required
        ></textarea>
      </div>

      <div class="form-actions">
        <button type="button" class="btn-cancel" @click="router.back()">취소</button>
        <button type="submit" class="btn-submit">등록하기</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const title = ref('');
const content = ref('');
const category = ref('FREE');
const selectedLaptopId = ref('');
const wishlist = ref([]);

// Load wishlist from localStorage
onMounted(() => {
  const savedWishlist = localStorage.getItem('wishlist');
  if (savedWishlist) {
    wishlist.value = JSON.parse(savedWishlist);
  }
});

const formatPrice = (price) => {
  return price ? price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '0';
};

const submitPost = async () => {
  try {
    // Validate required fields
    if (!title.value.trim()) {
      alert('제목을 입력해주세요.');
      return;
    }
    if (!content.value.trim()) {
      alert('내용을 입력해주세요.');
      return;
    }

    const userData = localStorage.getItem('user');
    const token = userData ? JSON.parse(userData)?.access : null;

    if (!token) {
      alert('로그인이 필요한 서비스입니다.');
      router.push('/login');
      return;
    }

    // For estimate posts, validate laptop selection
    if (category.value === 'ESTIMATE') {
      if (!selectedLaptopId.value) {
        alert('견적 문의를 위해 노트북을 선택해주세요.');
        return;
      }
      const selectedLaptop = wishlist.value.find(laptop => laptop.id === selectedLaptopId.value);
      if (!selectedLaptop) {
        alert('유효하지 않은 노트북이 선택되었습니다. 다시 선택해주세요.');
        return;
      }
    }

    // Prepare the request data
    const requestData = {
      title: title.value,
      content: content.value,
      category: category.value.toLowerCase(),  // Convert to lowercase to match backend expectations
      // Add laptop ID for estimate posts
      ...(category.value === 'ESTIMATE' && { laptop: selectedLaptopId.value })
    };

    // Make the API request
    const response = await axios.post(
      'http://localhost:8000/articles/',
      requestData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.status === 201) {
      alert('게시글이 성공적으로 등록되었습니다.');
      router.push('/community');
    } else {
      throw new Error('게시글 등록에 실패했습니다.');
    }
  } catch (error) {
    console.error('Error submitting post:', error);
    if (error.response) {
      // Server responded with an error
      console.error('Error response data:', error.response.data);
      console.error('Error status:', error.response.status);
      
      // Show more specific error messages based on the response
      if (error.response.status === 400) {
        alert(`입력한 내용을 확인해주세요: ${JSON.stringify(error.response.data)}`);
      } else if (error.response.status === 401) {
        alert('로그인이 만료되었습니다. 다시 로그인해주세요.');
        router.push('/login');
      } else {
        alert(`게시글 등록 중 오류가 발생했습니다: ${error.response.data?.detail || error.message}`);
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
      alert('서버로부터 응답이 없습니다. 네트워크 연결을 확인해주세요.');
    } else {
      // Something happened in setting up the request
      console.error('Request setup error:', error.message);
      alert(`게시글 등록 중 오류가 발생했습니다: ${error.message}`);
    }
  }
}
</script>

<style scoped>
.required {
  color: #ff4d4f;
  margin-left: 4px;
}

.help-text {
  color: #666;
  font-size: 13px;
  margin: 6px 0 12px;
  line-height: 1.5;
}

.error-text {
  color: #ff4d4f;
  font-size: 13px;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.estimate-note {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin: 20px 0;
}

.info-box {
  display: flex;
  gap: 12px;
  color: #2f3a45;
}

.info-box i {
  color: #1e6fd7;
  font-size: 20px;
  margin-top: 4px;
}

.info-box strong {
  display: block;
  margin-bottom: 8px;
  color: #1e6fd7;
}

.info-box ul {
  margin: 8px 0 0 20px;
  padding: 0;
}

.info-box li {
  margin-bottom: 4px;
  font-size: 13px;
  color: #555;
}

.write-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

.write-header {
  margin-bottom: 30px;
  text-align: center;
}

.write-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.write-header p {
  color: #888;
  font-size: 14px;
}

.write-form {
  background: #ffffff;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #eee;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #444;
  margin-bottom: 8px;
}

/* Input & Select & Textarea 공통 스타일 */
input[type="text"],
select,
textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  color: #333;
  transition: all 0.2s ease;
  background-color: #fafafa;
  box-sizing: border-box; /* 패딩 포함 크기 조절 */
}

input[type="text"]:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #1976d2;
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

textarea {
  resize: vertical; /* 세로로만 조절 가능 */
  line-height: 1.6;
}

/* 버튼 스타일 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 40px;
}

.btn-cancel {
  padding: 12px 24px;
  background-color: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel:hover {
  background-color: #e0e0e0;
}

.btn-submit {
  padding: 12px 32px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.btn-submit:hover {
  background-color: #1565c0;
  transform: translateY(-1px);
}

.btn-submit:active {
  transform: translateY(0);
}

/* 모바일 대응 */
@media (max-width: 600px) {
  .write-form {
    padding: 20px;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn-cancel, .btn-submit {
    width: 100%;
  }
}
</style>