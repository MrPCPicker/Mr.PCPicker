<template>
  <div class="post-edit">
    <div class="edit-header">
      <h1>게시글 수정</h1>
    </div>
    
    <form @submit.prevent="updatePost" class="edit-form">
      <div class="form-group">
        <input 
          v-model="post.title" 
          type="text" 
          class="title-input"
          placeholder="제목을 입력하세요" 
          required
        >
      </div>
      
      <div class="form-group content-group">
        <textarea 
          v-model="post.content" 
          class="content-input"
          placeholder="내용을 입력하세요" 
          required
        ></textarea>
      </div>

      <div class="form-actions">
        <button type="button" @click="$router.back()" class="btn-cancel">
          취소
        </button>
        <button type="submit" class="btn-submit">
          수정 완료
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const postId = route.params.id;

const post = ref({
  title: '',
  content: ''
});

// 기존 게시글 정보 가져오기
const fetchPost = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/articles/${postId}/`);
    post.value.title = response.data.title;
    post.value.content = response.data.content;
  } catch (error) {
    alert('게시글을 불러올 수 없습니다.');
    router.back();
  }
};

// 수정 요청 보내기
const updatePost = async () => {
  const userData = localStorage.getItem('user');
  const token = userData ? JSON.parse(userData).access : null;

  try {
    await axios.put(
      `http://localhost:8000/articles/${postId}/`,
      post.value,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    alert('수정되었습니다.');
    router.push(`/community/${postId}`); // 수정 후 상세페이지로 이동
  } catch (error) {
    alert('수정 권한이 없거나 오류가 발생했습니다.');
  }
};

onMounted(fetchPost);
</script>

<style scoped>
.post-edit {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.edit-header {
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.edit-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.edit-form {
  padding: 0 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.title-input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1.25rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 1rem;
  transition: border-color 0.2s;
}

.title-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

.content-group {
  min-height: 300px;
}

.content-input {
  width: 100%;
  min-height: 300px;
  padding: 1rem;
  font-size: 1rem;
  line-height: 1.6;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  resize: vertical;
  transition: border-color 0.2s;
}

.content-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  margin-top: 2rem;
}

.btn-submit,
.btn-cancel {
  padding: 0.6rem 1.25rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-submit {
  background-color: #1976d2;
  color: white;
}

.btn-submit:hover {
  background-color: #1565c0;
}

.btn-cancel {
  background-color: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background-color: #e0e0e0;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .post-edit {
    margin: 0;
    border-radius: 0;
    padding: 1rem;
  }
  
  .edit-header h1 {
    font-size: 1.25rem;
  }
  
  .title-input {
    font-size: 1.1rem;
  }
  
  .form-actions {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 1rem;
    margin: 0;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    z-index: 100;
  }
  
  .content-group {
    padding-bottom: 80px; /* 버튼 공간 확보 */
  }
}
</style>