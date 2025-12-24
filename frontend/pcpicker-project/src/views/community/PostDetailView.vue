<template>
  <div class="post-detail">
    <div class="post-header">
      <div class="post-category-tag" v-if="post.category">
        {{ translateCategory(post.category) }}
      </div>

      <div class="post-title-row">
        <h1>{{ post.title }}</h1>
        <div v-if="isPostAuthor" class="post-edit-delete">
          <button @click="editPost" class="btn-text">수정</button>
          <button @click="deletePost" class="btn-text delete">삭제</button>
        </div>
      </div>
      
      <div class="post-meta">
        <span class="author"><strong>{{ post.author?.username }}</strong></span>
        <span class="date">{{ formatDate(post.created_at) }}</span>
        <span class="views">조회 {{ post.views || 0 }}</span>
      </div>
    </div>

    <div class="post-content">
      <div v-if="displayLaptops.length > 0" class="laptop-section">
        <label class="section-label"><i class="fas fa-laptop"></i> 선택된 노트북 목록</label>
        <div class="selected-laptops">
          <div v-for="laptop in displayLaptops" :key="laptop.id" class="laptop-card">
            <span class="laptop-name">{{ laptop.name || laptop.model_name }}</span>
            <span class="laptop-price">{{ formatPrice(laptop.price) }}</span>
          </div>
        </div>
      </div>
      
      <div class="post-body" v-html="post.content"></div>
    </div>

    <div class="post-actions">
      <div class="like-container">
        <button 
          class="like-button" 
          :class="{ 'liked': isLiked }" 
          @click="toggleLike"
        >
          <i :class="[isLiked ? 'fas fa-heart' : 'far fa-heart']"></i>
          <span class="like-count">{{ post.like_count ?? 0 }}</span>
        </button>
      </div>
      <router-link to="/community" class="back-button">목록으로</router-link>
    </div>

    <div class="comment-section">
      <h3>댓글 <span>{{ comments.length }}</span></h3>
      <div class="comment-write">
        <textarea v-model="newComment" placeholder="따뜻한 댓글을 남겨주세요." rows="3"></textarea>
        <div class="comment-write-actions">
          <button class="btn-comment-submit" @click="createComment">댓글 등록</button>
        </div>
      </div>
      <div class="comment-list">
        <div v-for="comment in comments" :key="comment?.id" class="comment-item">
          <div class="comment-item-header">
            <span class="comment-author">{{ comment?.author?.username || '알 수 없는 사용자' }}</span>
            <span class="comment-date">{{ formatDate(comment?.created_at) }}</span>
          </div>
          <div v-if="editingId !== comment?.id" class="comment-content">{{ comment?.content }}</div>
          <div v-if="isCommentAuthor(comment)" class="comment-actions">
            <template v-if="editingId !== comment.id">
              <button @click="startEdit(comment)">수정</button>
              <button @click="deleteComment(comment.id)">삭제</button>
            </template>
            <div v-else class="comment-edit-form">
              <textarea v-model="editContent" rows="2"></textarea>
              <div class="edit-actions">
                <button class="btn-save" @click="updateComment(comment.id)">저장</button>
                <button class="btn-cancel" @click="cancelEdit">취소</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AuthService from '@/services/AuthService';
import axios from 'axios';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

const route = useRoute();
const router = useRouter();
const postId = route.params.id;

const post = ref({ title: '', content: '', like_count: 0, author: null, laptops: [] });
const isLiked = ref(false);
const comments = ref([]);
const newComment = ref('');
const editingId = ref(null);
const editContent = ref('');

// --- 노트북 목록 매칭 로직 (가장 중요) ---
const displayLaptops = computed(() => {
  // 서버에서 온 데이터 (보통 ID 리스트 [1, 2, 3] 형태일 확률이 높음)
  const laptopData = post.value.laptops || post.value.selected_laptops || [];
  
  if (!Array.isArray(laptopData)) return [];

  // 만약 서버에서 이미 이름/가격 객체를 줬다면 그대로 사용
  if (laptopData.length > 0 && typeof laptopData[0] === 'object') {
    return laptopData;
  }

  // 서버에서 ID(숫자)만 줬다면 로컬스토리지의 wishlist에서 상세 정보를 찾음
  const savedWishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
  return laptopData.map(id => {
    return savedWishlist.find(l => l.id === id) || { name: '불러올 수 없는 모델', price: 0 };
  });
});

// --- 카테고리 한글 변환 로직 ---
const translateCategory = (cat) => {
  if (!cat) return '';
  const mapping = {
    'estimate': '견적질문',
    'notice': '공지사항',
    'qna': 'Q&A',
    'free': '자유게시판',
    'ESTIMATE': '견적질문',
    'NOTICE': '공지사항',
    'QNA': 'Q&A',
    'FREE': '자유게시판'
  };
  return mapping[cat] || cat;
};

const getCurrentUser = () => AuthService.getCurrentUser()?.user || null;

const isPostAuthor = computed(() => {
  const user = getCurrentUser();
  return user && post.value.author && (user.id == post.value.author.id || user.username === post.value.author.username);
});

const isCommentAuthor = (comment) => {
  const user = getCurrentUser();
  return user && comment?.author && (user.id == comment.author.id || user.username === comment.author.username);
};

const fetchPost = async () => {
  try {
    const user = AuthService.getCurrentUser();
    const headers = user?.access ? { 'Authorization': `Bearer ${user.access}` } : {};
    
    try {
      const response = await axios.get(`http://localhost:8000/articles/${postId}/`, { headers });
      post.value = response.data;
      isLiked.value = response.data.is_liked || response.data.liked || false;
      console.log("받아온 데이터 확인:", response.data);
      await fetchComments();
    } catch (error) {
      if (error.response?.status === 401 && user?.access) {
        // If we have a token but it's expired, try to refresh it
        try {
          await AuthService.refreshToken();
          // Retry the request with the new token
          const newUser = AuthService.getCurrentUser();
          const newHeaders = newUser?.access ? { 'Authorization': `Bearer ${newUser.access}` } : {};
          const response = await axios.get(`http://localhost:8000/articles/${postId}/`, { 
            headers: newHeaders 
          });
          post.value = response.data;
          isLiked.value = response.data.is_liked || response.data.liked || false;
          await fetchComments();
        } catch (refreshError) {
          // If refresh fails, redirect to login
          console.error('Token refresh failed:', refreshError);
          router.push('/login');
        }
      } else if (error.response?.status === 401) {
        // If no token was available, redirect to login
        router.push('/login');
      } else {
        // For other errors, log them and show a message
        console.error('Error fetching post:', error);
      }
    }
  } catch (error) {
    console.error('Error in fetchPost:', error);
  }
};

const toggleLike = async () => {
  const user = AuthService.getCurrentUser();
  if (!user) { alert('로그인이 필요합니다.'); router.push('/login'); return; }
  try {
    const headers = { 'Authorization': `Bearer ${user.access}`, 'Content-Type': 'application/json' };
    const res = await axios.post(`http://localhost:8000/articles/${postId}/like/`, {}, { headers });
    if (res.data) {
      post.value = { ...post.value, like_count: res.data.like_count ?? res.data.count ?? 0 };
      isLiked.value = res.data.is_liked ?? res.data.liked ?? false;
    }
  } catch (err) {
    if (err.response?.status === 401) {
      await AuthService.refreshToken();
      await toggleLike();
    }
  }
};

const fetchComments = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/articles/${postId}/comments/`);
    comments.value = Array.isArray(response.data) ? response.data : response.data.results || [];
  } catch (error) {}
};

const createComment = async () => {
  if (!AuthService.getCurrentUser() || !newComment.value.trim()) return;
  try {
    await axios.post(`http://localhost:8000/articles/${postId}/comments/`, { content: newComment.value }, { headers: AuthService.getAuthHeader() });
    newComment.value = '';
    await fetchComments();
  } catch (error) {}
};

const startEdit = (comment) => { editingId.value = comment.id; editContent.value = comment.content; };
const cancelEdit = () => { editingId.value = null; editContent.value = ''; };
const updateComment = async (id) => {
  try {
    await axios.put(`http://localhost:8000/articles/comments/${id}/`, { content: editContent.value }, { headers: AuthService.getAuthHeader() });
    editingId.value = null;
    await fetchComments();
  } catch (error) {}
};
const deleteComment = async (id) => {
  if (!confirm('삭제하시겠습니까?')) return;
  try {
    await axios.delete(`http://localhost:8000/articles/comments/${id}/`, { headers: AuthService.getAuthHeader() });
    await fetchComments();
  } catch (error) {}
};
const deletePost = async () => {
  if (!confirm('게시글을 삭제하시겠습니까?')) return;
  try {
    await axios.delete(`http://localhost:8000/articles/${postId}/`, { headers: AuthService.getAuthHeader() });
    router.push('/community');
  } catch (error) {}
};
const editPost = () => {
  if (!isPostAuthor.value) {
    alert('수정 권한이 없습니다.');
    return;
  }
  router.push(`/community/edit/${postId}`);
};
const formatDate = (date) => date ? format(new Date(date), 'yyyy.MM.dd HH:mm', { locale: ko }) : '';
const formatPrice = (price) => price ? price.toLocaleString() + '원' : '가격 정보 없음';

onMounted(fetchPost);
</script>

<style scoped>
.post-detail { max-width: 850px; margin: 40px auto; padding: 0 20px; font-family: 'Pretendard', sans-serif; }

/* 1. 카테고리 태그 디자인 (이미지와 동일하게 둥근 형태) */
.post-category-tag {
  display: inline-block;
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 6px 18px;
  border-radius: 50px; /* 둥근 캡슐 모양 */
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 15px;
  border: 1px solid #bbdefb;
}

.post-header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
.post-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.post-title-row h1 { font-size: 28px; color: #222; margin: 0; font-weight: 700; }
.post-edit-delete { display: flex; gap: 12px; }
.btn-text { background: none; border: none; color: #999; font-size: 14px; cursor: pointer; text-decoration: underline; }
.post-meta { display: flex; gap: 20px; color: #888; font-size: 14px; }
.post-content { min-height: 250px; line-height: 1.8; font-size: 16px; margin-bottom: 50px; color: #333; }

/* 2. 노트북 정보 섹션 디자인 */
.laptop-section {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
}
.section-label { display: block; font-weight: 700; margin-bottom: 15px; color: #333; font-size: 15px; }
.selected-laptops { display: flex; flex-wrap: wrap; gap: 10px; }
.laptop-card {
  background: white;
  border: 1px solid #e0e0e0;
  padding: 10px 16px;
  border-radius: 8px;
  display: flex;
  gap: 15px;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.laptop-name { font-weight: 600; color: #333; }
.laptop-price { color: #d32f2f; font-weight: 700; font-size: 14px; }

.post-actions { display: flex; justify-content: space-between; border-top: 1px solid #eee; padding-top: 30px; margin-bottom: 50px; }

/* 좋아요 버튼 */
.like-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 1px solid #ddd;
  padding: 8px 18px;
  border-radius: 30px;
  cursor: pointer;
}
.like-button i { font-size: 18px; color: #ff4d4f; }
.like-count { font-weight: 700; color: #444; font-size: 15px; }
.like-button.liked { border-color: #ff4d4f; background-color: #fff1f0; }

.back-button { background: #1976d2; color: white; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; }

/* 댓글 섹션 */
.comment-section { background: #fcfcfc; border-radius: 12px; padding: 30px; border: 1px solid #eee; }
.comment-section h3 { font-size: 18px; margin-bottom: 25px; font-weight: 700; }
.comment-section h3 span { color: #1976d2; }
.comment-write { background: white; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 30px; }
.comment-write textarea { width: 100%; border: none; outline: none; resize: none; font-size: 14px; margin-bottom: 10px; }
.btn-comment-submit { background: #333; color: white; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; }
.comment-item { padding: 20px 0; border-bottom: 1px solid #eee; }
.comment-author { font-weight: 700; font-size: 15px; }
</style>