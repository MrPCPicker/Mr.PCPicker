<template>
  <div class="post-edit">
    <div class="edit-header">
      <h1>게시글 수정</h1>
    </div>
    
    <form @submit.prevent="updatePost" class="edit-form">
      <div class="form-group">
        <label for="category">카테고리</label>
        <div class="select-wrapper">
          <select id="category" v-model="post.category" disabled>
            <option value="notice">공지</option>
            <option value="qna">Q&A</option>
            <option value="estimate">견적 요청</option>
            <option value="free">자유게시판</option>
          </select>
        </div>
      </div>

      <div v-if="post.category === 'estimate'" class="form-group">
        <label>선택된 노트북</label>
        <div v-if="post.laptops && post.laptops.length > 0" class="selected-laptops">
          <div v-for="(laptop, index) in post.laptops" :key="index" class="laptop-tag">
            {{ laptop.name || laptop.model_name }} ({{ formatPrice(laptop.price) }}원)
          </div>
        </div>
        <div v-else class="empty-message">
          <i class="fas fa-exclamation-circle"></i> 
          선택된 노트북 정보가 없습니다.
        </div>
      </div>
      
      <div v-if="post.category === 'estimate'" class="form-group estimate-note">
        <div class="info-box">
          <i class="fas fa-lightbulb"></i>
          <div>
            <strong>견적에 대한 질문을 작성해주세요😁</strong>
            <ul>
              <li>이 정도면 가격이 괜찮은 편인가요?</li>
              <li>이 사양으로 영상 편집이 가능할까요?</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="title">제목</label>
        <input
          id="title"
          v-model="post.title"
          type="text"
          placeholder="제목을 입력하세요"
          required
        />
      </div>

      <div class="form-group">
        <label for="content">내용 <span class="required" v-if="post.category === 'estimate'">*</span></label>
        <textarea
          id="content"
          v-model="post.content"
          :placeholder="post.category === 'estimate' ? '구체적인 질문을 작성해주세요.' : '내용을 작성해 주세요.'"
          rows="12"
          required
        ></textarea>
      </div>

      <div class="form-actions">
        <button type="button" class="btn-cancel" @click="$router.back()">취소</button>
        <button type="submit" class="btn-submit">수정 완료</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const postId = route.params.id;

const post = ref({
  title: '',
  content: '',
  category: '',
  laptops: []
});

const formatPrice = (price) => {
  if (!price) return '0';
  return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

// 핵심: 작성자 권한 체크 및 데이터 로드
const fetchPost = async () => {
  try {
    const token = authStore.user?.access;
    if (!token) {
      alert('로그인이 필요합니다.');
      router.push('/login');
      return;
    }

    const response = await axios.get(`http://localhost:8000/articles/${postId}/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = response.data;

    // 1. 서버 응답에서 작성자 ID 추출 (객체/숫자 모두 대응)
    const authorId = typeof data.author === 'object' 
      ? (data.author.id || data.author.pk) 
      : data.author;

    // 2. 스토어에서 현재 로그인한 유저 ID 추출
    const currentUserId = authStore.user?.user_id || authStore.user?.id || authStore.user?.pk;

    // 3. 권한 검사 (둘 다 존재할 때만 비교)
    if (authorId && currentUserId) {
      if (String(authorId) !== String(currentUserId)) {
        alert('본인이 작성한 글만 수정할 수 있습니다.');
        router.back();
        return;
      }
    }

    // 4. 데이터 할당
    post.value = {
      title: data.title,
      content: data.content,
      category: data.category,
      laptops: data.laptops || []
    };
  } catch (error) {
    console.error('Fetch Error:', error);
    alert('게시글을 불러오는 중 오류가 발생했습니다.');
    router.back();
  }
};

const updatePost = async () => {
  const token = authStore.user?.access;
  try {
    // 팁: 수정 시에는 필요한 데이터만 전송 (laptops는 보통 PK 리스트만 보냄)
    // 서버 API 사양에 따라 노트북 객체 전체를 보낼지, ID만 보낼지 결정해야 함
    const payload = {
      title: post.value.title,
      content: post.value.content,
      category: post.value.category,
      // 노트북 수정이 불가능한 구조라면 제외하거나 기존 데이터 전송
      laptops: post.value.laptops.map(l => l.id || l.pk || l) 
    };

    await axios.put(`http://localhost:8000/articles/${postId}/`, payload, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    alert('성공적으로 수정되었습니다.');
    router.push(`/community/${postId}`);
  } catch (error) {
    console.error('Update Error:', error);
    const msg = error.response?.data?.detail || '수정 중 오류가 발생했습니다.';
    alert(msg);
  }
};

onMounted(fetchPost);
</script>

<style scoped>
/* 기존 스타일과 동일하되 가독성을 위해 일부 유지 */
.post-edit { max-width: 800px; margin: 2rem auto; padding: 2rem; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.form-group { margin-bottom: 1.5rem; }
label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
input, textarea, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; }
.laptop-tag { background: #e3f2fd; color: #1976d2; padding: 0.5rem; border-radius: 4px; margin-right: 0.5rem; display: inline-block; }
.btn-submit { background: #1976d2; color: white; border: none; padding: 0.75rem 1.5rem; cursor: pointer; border-radius: 4px; }
.btn-cancel { background: #eee; border: none; padding: 0.75rem 1.5rem; margin-right: 1rem; cursor: pointer; border-radius: 4px; }
</style>