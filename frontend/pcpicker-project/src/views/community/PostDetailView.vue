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
        <span class="views"><i class="far fa-eye"></i> {{ post.views || 0 }}</span>
      </div>
    </div>

    <div class="post-content">
      <div v-if="displayLaptops.length > 0" class="laptop-comparison-section">
        <label class="section-label">
          <i class="fas fa-microchip"></i> 비교 및 분석 대상 모델
        </label>
        <div class="laptop-grid">
          <div v-for="laptop in displayLaptops" :key="laptop.id" class="laptop-spec-card">
            <div class="laptop-img-box">
              <img :src="getItemImage(laptop)" alt="laptop">
            </div>
            <div class="laptop-details">
              <div class="laptop-name-row">
                <span class="laptop-name">{{ laptop.name || laptop.model_name }}</span>
                <span class="laptop-price">{{ formatPrice(laptop.price) }}</span>
              </div>
              <div class="laptop-spec-tags">
                <span v-for="spec in laptop.specs" :key="spec" class="spec-tag">{{ spec }}</span>
                <span v-if="!laptop.specs || laptop.specs.length === 0" class="spec-tag-empty">상세 스펙 정보 없음</span>
              </div>
              <a 
                v-if="laptop.shoppingUrl" 
                :href="laptop.shoppingUrl" 
                target="_blank"
                class="shop-link"
                rel="noopener noreferrer"
                @click.stop
              >
                <i class="fas fa-shopping-cart"></i> 구매 링크
              </a>
            </div>
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
      <div class="comment-header-row">
        <h3>댓글 <span>{{ comments.length }}</span></h3>
      </div>
      
      <div class="comment-write-box">
        <textarea v-model="newComment" placeholder="질문에 대한 조언이나 따뜻한 댓글을 남겨주세요." rows="3"></textarea>
        <div class="comment-write-footer">
          <button class="btn-comment-submit" @click="createComment">댓글 등록</button>
        </div>
      </div>

      <div class="comment-list">
        <div v-for="comment in comments" :key="comment?.id" class="comment-card">
          <div class="comment-card-header">
            <div class="comment-user-info">
              <div class="user-avatar"><i class="fas fa-user"></i></div>
              <div class="user-meta">
                <span class="comment-author">{{ comment?.author?.username || '알 수 없는 사용자' }}</span>
                <span class="comment-date">{{ formatDate(comment?.created_at) }}</span>
              </div>
            </div>
            <div v-if="isCommentAuthor(comment)" class="comment-actions-inline">
              <template v-if="editingId !== comment.id">
                <button @click="startEdit(comment)">수정</button>
                <button @click="deleteComment(comment.id)" class="del-text">삭제</button>
              </template>
            </div>
          </div>

          <div class="comment-body">
            <div v-if="editingId !== comment?.id" class="comment-text">{{ comment?.content }}</div>
            <div v-else class="comment-edit-form">
              <textarea v-model="editContent" rows="2"></textarea>
              <div class="edit-actions">
                <button class="btn-save" @click="updateComment(comment.id)">저장</button>
                <button class="btn-cancel" @click="cancelEdit">취소</button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="comments.length === 0" class="empty-comments">
          첫 번째 댓글을 남겨주세요!
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

// --- 데이터 헬퍼 함수 ---
const getItemImage = (item) => {
  if (!item) return 'https://via.placeholder.com/100';
  return item.image || item.imageUrl || 'https://via.placeholder.com/100?text=No+Image';
};
const formatPrice = (price) => {
  if (price === undefined || price === null) return '가격 정보 없음';
  return price.toLocaleString() + '원';
};
const formatDate = (date) => date ? format(new Date(date), 'yyyy.MM.dd HH:mm', { locale: ko }) : '';

// --- 노트북 목록 매칭 로직 (장바구니 데이터와 동기화) ---
const displayLaptops = computed(() => {
  const laptopData = post.value.laptops || post.value.selected_laptops || [];
  if (!Array.isArray(laptopData)) return [];

  // 장바구니 데이터 가져오기
  const savedWishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
  
  return laptopData.map(item => {
    // 아이템이 객체인지 ID만 있는지 확인
    const itemId = (typeof item === 'object') ? item.id : item;
    
    // 장바구니에서 해당 아이템 찾기
    const foundInWishlist = savedWishlist.find(l => l.id === itemId);
    
    // 장바구니에 있는 경우
    if (foundInWishlist) {
      return {
        id: foundInWishlist.id,
        name: foundInWishlist.title || foundInWishlist.name || foundInWishlist.model_name || `PC ${foundInWishlist.id}`,
        price: foundInWishlist.price || 0,
        specs: foundInWishlist.specs || [],
        image: foundInWishlist.image || foundInWishlist.imageUrl || 'https://via.placeholder.com/100',
        shoppingUrl: foundInWishlist.shoppingUrl || foundInWishlist.url || '#',
        model_name: foundInWishlist.model_name || ''
      };
    }
    
    // 장바구니에 없는 경우 (기본값)
    return {
      id: item.id || item,
      name: item.title || item.name || item.model_name || `PC ${item.id || item}`,
      price: item.price || 0,
      specs: item.specs || [],
      image: item.image || item.imageUrl || 'https://via.placeholder.com/100',
      shoppingUrl: item.shoppingUrl || item.url || '#',
      model_name: item.model_name || ''
    };
  });
});

// --- 카테고리 변환 ---
const translateCategory = (cat) => {
  const mapping = {
    'estimate': '견적질문', 'notice': '공지사항', 'qna': 'Q&A', 'free': '자유게시판',
    'ESTIMATE': '견적질문', 'NOTICE': '공지사항', 'QNA': 'Q&A', 'FREE': '자유게시판'
  };
  return mapping[cat] || cat;
};

// --- 권한 체크 ---
const getCurrentUser = () => AuthService.getCurrentUser()?.user || null;
const isPostAuthor = computed(() => {
  const user = getCurrentUser();
  return user && post.value.author && (user.id == post.value.author.id || user.username === post.value.author.username);
});
const isCommentAuthor = (comment) => {
  const user = getCurrentUser();
  return user && comment?.author && (user.id == comment.author.id || user.username === comment.author.username);
};

// --- API 통신 로직 ---
const fetchPost = async () => {
  try {
    const user = AuthService.getCurrentUser();
    const headers = user?.access ? { 'Authorization': `Bearer ${user.access}` } : {};
    const response = await axios.get(`http://localhost:8000/articles/${postId}/`, { headers });
    post.value = response.data;
    isLiked.value = response.data.is_liked || response.data.liked || false;
    await fetchComments();
  } catch (error) {
    if (error.response?.status === 401) router.push('/login');
    console.error('Error fetching post:', error);
  }
};

const fetchComments = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/articles/${postId}/comments/`);
    comments.value = Array.isArray(response.data) ? response.data : response.data.results || [];
  } catch (error) {}
};

const toggleLike = async () => {
  const user = AuthService.getCurrentUser();
  if (!user) { alert('로그인이 필요합니다.'); router.push('/login'); return; }
  try {
    const headers = { 'Authorization': `Bearer ${user.access}` };
    const res = await axios.post(`http://localhost:8000/articles/${postId}/like/`, {}, { headers });
    post.value.like_count = res.data.like_count ?? res.data.count ?? 0;
    isLiked.value = res.data.is_liked ?? res.data.liked ?? false;
  } catch (err) {}
};

const createComment = async () => {
  if (!AuthService.getCurrentUser() || !newComment.value.trim()) return;
  try {
    await axios.post(`http://localhost:8000/articles/${postId}/comments/`, { content: newComment.value }, { headers: AuthService.getAuthHeader() });
    newComment.value = '';
    await fetchComments();
  } catch (error) {}
};

const updateComment = async (id) => {
  try {
    await axios.put(`http://localhost:8000/articles/comments/${id}/`, { content: editContent.value }, { headers: AuthService.getAuthHeader() });
    editingId.value = null;
    await fetchComments();
  } catch (error) {}
};

const deleteComment = async (id) => {
  if (!confirm('댓글을 삭제하시겠습니까?')) return;
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

const editPost = () => router.push(`/community/edit/${postId}`);
const startEdit = (comment) => { editingId.value = comment.id; editContent.value = comment.content; };
const cancelEdit = () => { editingId.value = null; editContent.value = ''; };

onMounted(fetchPost);
</script>

<style scoped>
.post-detail { max-width: 850px; margin: 40px auto; padding: 0 20px; font-family: 'Pretendard', sans-serif; color: #333; }

/* 헤더 디자인 */
.post-header { border-bottom: 2px solid #333; padding-bottom: 24px; margin-bottom: 35px; }
.post-category-tag {
  display: inline-block; background-color: #e3f2fd; color: #1976d2;
  padding: 6px 18px; border-radius: 50px; font-size: 13px; font-weight: 700; margin-bottom: 15px;
}
.post-title-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; margin-bottom: 15px; }
.post-title-row h1 { font-size: 30px; line-height: 1.4; margin: 0; font-weight: 800; color: #111; }
.post-meta { display: flex; gap: 20px; color: #888; font-size: 14px; }
.post-edit-delete { display: flex; gap: 12px; flex-shrink: 0; padding-top: 10px; }
.btn-text { background: none; border: none; color: #aaa; font-size: 14px; cursor: pointer; text-decoration: underline; }
.btn-text.delete:hover { color: #ff4d4f; }

/* 노트북 비교 섹션 (개선된 카드형) */
.laptop-comparison-section {
  background: #f1f4f9; border-radius: 16px; padding: 24px; margin-bottom: 40px; border: 1px solid #e2e8f0;
}
.section-label {
  display: flex; align-items: center; gap: 8px; font-weight: 800; color: #1a73e8; margin-bottom: 20px; font-size: 16px;
}
.laptop-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 16px; }
.laptop-spec-card {
  display: flex; background: #ffffff; border-radius: 12px; padding: 16px; border: 1px solid #e0e6ed;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: 0.2s;
}
.laptop-spec-card:hover { transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0,0,0,0.08); }
.laptop-img-box {
  width: 90px; height: 70px; flex-shrink: 0; margin-right: 15px;
  background: #f8f9fa; border-radius: 8px; padding: 5px;
}
.laptop-img-box img { width: 100%; height: 100%; object-fit: contain; }
.laptop-details { flex: 1; min-width: 0; }
.laptop-name-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.laptop-name { font-weight: 700; color: #222; font-size: 15px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.laptop-price { color: #d32f2f; font-weight: 800; font-size: 14px; white-space: nowrap; margin-left: 10px; }
.laptop-spec-tags { display: flex; flex-wrap: wrap; gap: 5px; margin: 8px 0; }
.spec-tag { background: #f0f7ff; color: #4a6fa5; font-size: 11px; padding: 3px 8px; border-radius: 4px; border: 1px solid #d1e3f8; }
.spec-tag-empty { color: #bbb; font-size: 12px; }

.shop-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 6px 12px;
  background-color: #1976d2;
  color: white !important;
  border-radius: 4px;
  font-size: 13px;
  text-decoration: none;
  transition: background-color 0.2s;
}

.shop-link:hover {
  background-color: #1565c0;
  text-decoration: none;
}

.shop-link i {
  font-size: 12px;
}

/* 본문 영역 */
.post-content { min-height: 300px; margin-bottom: 50px; }
.post-body { line-height: 1.8; font-size: 17px; color: #333; white-space: pre-wrap; }

/* 하단 버튼 */
.post-actions { display: flex; justify-content: space-between; border-top: 1px solid #eee; padding-top: 30px; margin-bottom: 50px; }
.like-button {
  display: flex; align-items: center; gap: 10px; background: white; border: 1px solid #ddd; padding: 10px 22px; border-radius: 50px; cursor: pointer; transition: 0.2s;
}
.like-button i { font-size: 20px; color: #ff4d4f; }
.like-button.liked { background: #fff1f0; border-color: #ff4d4f; }
.like-count { font-weight: 800; color: #444; font-size: 16px; }
.back-button { background: #2f3a45; color: white; padding: 12px 28px; border-radius: 10px; text-decoration: none; font-weight: 700; transition: 0.2s; }
.back-button:hover { background: #1a73e8; }

/* 댓글 섹션 디자인 */
.comment-section { background: #fff; border-top: 1px solid #eee; padding-top: 40px; }
.comment-header-row h3 { font-size: 20px; font-weight: 800; margin-bottom: 25px; }
.comment-header-row span { color: #1a73e8; }

.comment-write-box {
  background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 12px; padding: 18px; margin-bottom: 40px;
}
.comment-write-box textarea {
  width: 100%; border: none; background: transparent; resize: none; font-size: 15px; outline: none; font-family: inherit;
}
.comment-write-footer { display: flex; justify-content: flex-end; margin-top: 12px; }
.btn-comment-submit { background: #1a73e8; color: white; border: none; padding: 10px 25px; border-radius: 8px; font-weight: 700; cursor: pointer; }

.comment-card { padding: 25px 0; border-bottom: 1px solid #f1f3f5; }
.comment-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.comment-user-info { display: flex; align-items: center; gap: 12px; }
.user-avatar { width: 40px; height: 40px; background: #eef2f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #94a3b8; }
.user-meta { display: flex; flex-direction: column; }
.comment-author { font-weight: 700; font-size: 15px; color: #1e293b; }
.comment-date { font-size: 12px; color: #94a3b8; margin-top: 2px; }

.comment-actions-inline { display: flex; gap: 12px; }
.comment-actions-inline button { background: none; border: none; font-size: 13px; color: #94a3b8; cursor: pointer; text-decoration: underline; }
.comment-actions-inline .del-text:hover { color: #ef4444; }

.comment-text { line-height: 1.6; color: #334155; font-size: 15px; padding-left: 52px; white-space: pre-wrap; }

.comment-edit-form { padding-left: 52px; }
.comment-edit-form textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 10px; }
.edit-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-save { background: #1a73e8; color: white; border: none; padding: 6px 15px; border-radius: 4px; cursor: pointer; }
.btn-cancel { background: #eee; border: none; padding: 6px 15px; border-radius: 4px; cursor: pointer; }

.empty-comments { text-align: center; padding: 40px; color: #bbb; font-size: 15px; }
</style>