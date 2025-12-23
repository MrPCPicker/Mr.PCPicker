<template>
  <div class="post-detail">
    <div class="post-header">
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
      <div class="post-body" v-html="post.content"></div>
    </div>

    <div class="post-actions">
      <button class="like-button" :class="{ 'liked': isLiked }" @click="toggleLike">
        <i :class="[isLiked ? 'fas fa-heart' : 'far fa-heart']"></i>
        <span>좋아요</span>
      </button>
      <router-link to="/community" class="back-button">목록으로</router-link>
    </div>

    <div class="comment-section">
      <h3>댓글 <span>{{ comments.length }}</span></h3>
      
      <div class="comment-write">
        <textarea 
          v-model="newComment" 
          placeholder="따뜻한 댓글을 남겨주세요."
          rows="3"
        ></textarea>
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

          <div v-if="editingId !== comment?.id" class="comment-content">
            {{ comment?.content }}
          </div>
          
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

// 상태 관리
const post = ref({
  like_count: 0,
  author: null
});
const isLiked = ref(false);
const comments = ref([]);
const newComment = ref('');
const editingId = ref(null);
const editContent = ref('');

// --- 인증 로직 ---
const getCurrentUser = () => AuthService.getCurrentUser()?.user || null;

const isPostAuthor = computed(() => {
  const user = getCurrentUser();
  if (!user || !post.value?.author) return false;
  return (user.username === post.value.author.username) || (user.id == post.value.author.id);
});

const isCommentAuthor = (comment) => {
  const user = getCurrentUser();
  if (!user || !comment?.author) return false;
  return (user.username === comment.author.username) || (user.id == comment.author.id);
};

// --- API 함수 ---

const fetchPost = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/articles/${postId}/`, {
      headers: AuthService.getAuthHeader()
    });
    post.value = response.data;
    isLiked.value = response.data.is_liked || response.data.liked || false;
    await fetchComments(); 
  } catch (error) {
    console.error('게시글 로드 실패:', error);
  }
};

const toggleLike = async () => {
  if (!AuthService.getCurrentUser()) {
    alert('로그인이 필요합니다.');
    return;
  }

  try {
    const res = await axios.post(`http://localhost:8000/articles/${postId}/like/`, {}, {
      headers: AuthService.getAuthHeader()
    });

    // 서버 응답 데이터를 화면에 즉시 반영
    if (res.data) {
      post.value.like_count = res.data.like_count;
      isLiked.value = res.data.is_liked !== undefined ? res.data.is_liked : res.data.liked;
    }
  } catch (err) {
    console.error('좋아요 토글 실패:', err);
    alert('좋아요 처리 중 오류가 발생했습니다.');
  }
};

const fetchComments = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/articles/${postId}/comments/`);
    comments.value = Array.isArray(response.data) ? response.data : response.data.results || [];
  } catch (error) {
    console.error('댓글 로드 실패:', error);
  }
};

const createComment = async () => {
  if (!AuthService.getCurrentUser()) { alert('로그인이 필요합니다.'); return; }
  if (!newComment.value.trim()) return;

  try {
    await axios.post(
      `http://localhost:8000/articles/${postId}/comments/`,
      { content: newComment.value },
      { headers: AuthService.getAuthHeader() }
    );
    newComment.value = '';
    await fetchComments(); 
  } catch (error) {
    alert('댓글 등록 실패');
  }
};

const startEdit = (comment) => {
  editingId.value = comment.id;
  editContent.value = comment.content;
};

const cancelEdit = () => {
  editingId.value = null;
  editContent.value = '';
};

const updateComment = async (commentId) => {
  try {
    await axios.put(
      `http://localhost:8000/articles/comments/${commentId}/`,
      { content: editContent.value },
      { headers: AuthService.getAuthHeader() }
    );
    editingId.value = null;
    await fetchComments();
  } catch (error) {
    alert('댓글 수정 실패');
  }
};

const deleteComment = async (commentId) => {
  if (!confirm('정말로 삭제하시겠습니까?')) return;
  try {
    await axios.delete(`http://localhost:8000/articles/comments/${commentId}/`, {
      headers: AuthService.getAuthHeader()
    });
    await fetchComments();
  } catch (error) {
    alert('댓글 삭제 실패');
  }
};

const deletePost = async () => {
  if (!confirm('게시글을 삭제하시겠습니까?')) return;
  try {
    await axios.delete(`http://localhost:8000/articles/${postId}/`, {
      headers: AuthService.getAuthHeader()
    });
    router.push('/community');
  } catch (error) {
    alert('게시글 삭제 실패');
  }
};

const editPost = () => {
  router.push(`/community/edit/${postId}`);
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return format(new Date(dateString), 'yyyy.MM.dd HH:mm', { locale: ko });
};

onMounted(fetchPost);
</script>

<style scoped>
.post-detail { max-width: 850px; margin: 40px auto; padding: 0 20px; font-family: 'Pretendard', sans-serif; }

/* 게시글 헤더 */
.post-header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
.post-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.post-title-row h1 { font-size: 28px; color: #222; margin: 0; font-weight: 700; }

.post-edit-delete { display: flex; gap: 12px; }
.btn-text { background: none; border: none; color: #999; font-size: 14px; cursor: pointer; text-decoration: underline; }
.btn-text:hover { color: #1976d2; }
.btn-text.delete:hover { color: #d32f2f; }

.post-meta { display: flex; gap: 20px; color: #888; font-size: 14px; }
.post-meta .author { color: #333; }

/* 본문 */
.post-content { min-height: 250px; line-height: 1.8; font-size: 16px; margin-bottom: 50px; color: #333; }

/* 액션 바 */
.post-actions { display: flex; justify-content: space-between; border-top: 1px solid #eee; padding-top: 30px; margin-bottom: 50px; }

/* 하트 좋아요 버튼 커스텀 디자인 */
.like-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 2px solid #ff4d4f; /* 선명한 레드 테두리 */
  padding: 10px 20px;
  border-radius: 50px; /* 캡슐 모양 */
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
  color: #ff4d4f;
}

.like-button i {
  font-size: 20px;
  color: #ff4d4f;
}

/* 눌렀을 때(Liked) 상태 디자인 */
.like-button.liked {
  background: #ff4d4f;
  color: white;
}

.like-button.liked i {
  color: white; /* 배경이 빨간색일 때 하트는 흰색으로 */
}

.like-button:hover {
  transform: scale(1.05); /* 마우스 올리면 살짝 커짐 */
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.2);
}

.back-button { background: #1976d2; color: white; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; }

/* 댓글 섹션 (기존 디자인 유지) */
.comment-section { background: #fcfcfc; border-radius: 12px; padding: 30px; border: 1px solid #eee; }
.comment-section h3 { font-size: 18px; margin-bottom: 25px; font-weight: 700; }
.comment-section h3 span { color: #1976d2; }

.comment-write { background: white; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.comment-write textarea { width: 100%; border: none; outline: none; resize: none; font-size: 14px; margin-bottom: 10px; }
.comment-write-actions { display: flex; justify-content: flex-end; }
.btn-comment-submit { background: #333; color: white; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; }

.comment-item { padding: 20px 0; border-bottom: 1px solid #eee; }
.comment-item:last-child { border-bottom: none; }
.comment-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.comment-author { font-weight: 700; font-size: 15px; color: #333; }
.comment-date { font-size: 13px; color: #aaa; }
.comment-content { font-size: 15px; color: #444; line-height: 1.6; margin-bottom: 12px; white-space: pre-wrap; }

.comment-actions { display: flex; gap: 12px; }
.comment-actions button { background: none; border: none; color: #aaa; font-size: 13px; cursor: pointer; text-decoration: underline; padding: 0; }
.comment-actions button:hover { color: #666; }

.comment-edit-form { width: 100%; background: #f0f0f0; padding: 15px; border-radius: 8px; }
.comment-edit-form textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; resize: none; margin-bottom: 10px; }
.edit-actions { display: flex; justify-content: flex-end; gap: 8px; }
.btn-save { background: #3f404162; color: white; border: none; padding: 6px 16px; border-radius: 4px; cursor: pointer; }
.btn-cancel { background: #ccc; color: white; border: none; padding: 6px 16px; border-radius: 4px; cursor: pointer; }
</style>