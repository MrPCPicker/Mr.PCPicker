<template>
  <div class="write-container">
    <h1>글쓰기</h1>

    <form @submit.prevent="submitPost">
      <select v-model="category">
        <option value="notice">공지사항</option>
        <option value="qna">Q&A</option>
        <option value="free">자유게시판</option>
      </select>

      <input
        v-model="title"
        type="text"
        placeholder="제목을 입력하세요"
        required
      />

      <textarea
        v-model="content"
        placeholder="내용을 입력하세요"
        rows="10"
        required
      ></textarea>

      <button type="submit">등록</button>
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
    await axios.post(
      '/api/articles/',
      {
        title: title.value,
        content: content.value,
        category: category.value,
      },
      {
        headers: {
          Authorization: `Bearer ${JSON.parse(localStorage.getItem('user'))?.access}`,
        },
      }
    )

    alert('게시글이 등록되었습니다.')
    router.push('/community')
  } catch (error) {
    alert('게시글 등록에 실패했습니다.')
    console.error(error)
  }
}
</script>
