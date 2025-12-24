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

const post = ref({ title: '', content: '', like_count: 0, author: null });
const isLiked = ref(false);
const comments = ref([]);
const newComment = ref('');
const editingId = ref(null);
const editContent = ref('');

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
    const response = await axios.get(`http://localhost:8000/articles/${postId}/`, { headers });
    post.value = response.data;
    isLiked.value = response.data.is_liked || response.data.liked || false;
    await fetchComments();
  } catch (error) {
    if (error.response?.status === 401) router.push('/login');
  }
};

// --- 좋아요 즉시 반영 로직 ---
const toggleLike = async () => {
  const user = AuthService.getCurrentUser();
  if (!user) {
    alert('로그인이 필요합니다.');
    router.push('/login');
    return;
  }

  try {
    const headers = { 
      'Authorization': `Bearer ${user.access}`,
      'Content-Type': 'application/json' 
    };

    const res = await axios.post(`http://localhost:8000/articles/${postId}/like/`, {}, { headers });

    if (res.data) {
      // 1. 서버 응답값 추출
      const newCount = res.data.like_count ?? res.data.count ?? 0;
      const newIsLiked = res.data.is_liked ?? res.data.liked ?? false;

      // 2. [중요] 객체 자체를 새로 할당하여 Vue의 반응성을 강제로 깨움 (UI 즉시 업데이트)
      post.value = {
        ...post.value,
        like_count: newCount
      };
      isLiked.value = newIsLiked;
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
  if (!confirm('삭제하시겠습니까?')) return;
  try {
    await axios.delete(`http://localhost:8000/articles/${postId}/`, { headers: AuthService.getAuthHeader() });
    router.push('/community');
  } catch (error) {}
};
const editPost = () => router.push(`/community/edit/${postId}`);
const formatDate = (date) => date ? format(new Date(date), 'yyyy.MM.dd HH:mm', { locale: ko }) : '';

onMounted(fetchPost);
</script>

<style scoped>
.post-detail { max-width: 850px; margin: 40px auto; padding: 0 20px; font-family: 'Pretendard', sans-serif; }
.post-header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
.post-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.post-title-row h1 { font-size: 28px; color: #222; margin: 0; font-weight: 700; }
.post-edit-delete { display: flex; gap: 12px; }
.btn-text { background: none; border: none; color: #999; font-size: 14px; cursor: pointer; text-decoration: underline; }
.post-meta { display: flex; gap: 20px; color: #888; font-size: 14px; }
.post-content { min-height: 250px; line-height: 1.8; font-size: 16px; margin-bottom: 50px; color: #333; }
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
  transition: all 0.2s ease;
}
.like-button i { font-size: 18px; color: #ff4d4f; }
.like-count { font-weight: 700; color: #444; font-size: 15px; }
.like-button:hover { background-color: #fff1f0; border-color: #ffccc7; transform: translateY(-2px); }
.like-button.liked { border-color: #ff4d4f; background-color: #fff1f0; }
.like-button.liked .like-count { color: #ff4d4f; }
.like-button:active { transform: scale(0.9); }

.back-button { background: #1976d2; color: white; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; }
.comment-section { background: #fcfcfc; border-radius: 12px; padding: 30px; border: 1px solid #eee; }
.comment-section h3 { font-size: 18px; margin-bottom: 25px; font-weight: 700; }
.comment-section h3 span { color: #1976d2; }
.comment-write { background: white; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 30px; }
.comment-write textarea { width: 100%; border: none; outline: none; resize: none; font-size: 14px; }
.btn-comment-submit { background: #333; color: white; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; }
.comment-item { padding: 20px 0; border-bottom: 1px solid #eee; }
.comment-author { font-weight: 700; font-size: 15px; }
.comment-actions button { background: none; border: none; color: #aaa; font-size: 13px; cursor: pointer; text-decoration: underline; margin-right: 10px; }
</style>