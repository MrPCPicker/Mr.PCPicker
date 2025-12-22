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
            <option value="notice">공지사항</option>
            <option value="qna">Q&A</option>
            <option value="free">자유게시판</option>
          </select>
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
        <label for="content">내용</label>
        <textarea
          id="content"
          v-model="content"
          placeholder="내용을 작성해 주세요."
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
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const title = ref('')
const content = ref('')
const category = ref('free')

const submitPost = async () => {
  try {
    const userData = localStorage.getItem('user');
    const token = userData ? JSON.parse(userData)?.access : null;

    if (!token) {
      alert('로그인이 필요한 서비스입니다.');
      router.push('/login');
      return;
    }

    await axios.post(
      'http://localhost:8000/articles/', // API 주소 확인 필요
      {
        title: title.value,
        content: content.value,
        category: category.value,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    alert('게시글이 성공적으로 등록되었습니다.')
    router.push('/community')
  } catch (error) {
    alert('게시글 등록에 실패했습니다. 내용을 다시 확인해 주세요.')
    console.error(error)
  }
}
</script>

<style scoped>
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