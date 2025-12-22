<template>
  <div class="community-container">
    <div class="page-header">
      <h1>커뮤니티 게시판</h1>
      <div class="page-header-controls">
        <div class="page-info">
          <span>총 <strong>{{ totalPosts }}</strong>개의 게시글</span>
          <span class="page-divider">|</span>
          <span class="page-number">{{ currentPage }} / {{ totalPages }} 페이지</span>
        </div>
        <button 
          v-if="isAuthenticated" 
          class="write-button-top" 
          @click="writePost"
        >
          <i class="fas fa-pen"></i>
          <span>글쓰기</span>
        </button>
      </div>
    </div>

    <div class="category-filter">
      <button 
        v-for="category in categories" 
        :key="category.value"
        :class="{ 'active': selectedCategory === category.value }"
        @click="filterByCategory(category.value)"
      >
        {{ category.label }}
      </button>
    </div>

    <div class="post-list">
      <div v-if="loading" class="loading">로딩 중...</div>
      <div v-else-if="posts.length === 0" class="no-posts">
        게시글이 없습니다.
      </div>
      <div 
        v-else
        v-for="post in posts" 
        :key="post.id" 
        class="post-item"
      >
        <div class="post-category" :class="getCategoryClass(post.category)">
          {{ getCategoryLabel(post.category) }}
        </div>
        <div class="post-content">
          <router-link :to="`/community/${post.id}`" class="post-title">
            {{ post.title }}
          </router-link>
          <p class="post-desc">{{ post.content.substring(0, 100) }}{{ post.content.length > 100 ? '...' : '' }}</p>
          <div class="post-meta">
            <span class="post-author">{{ post.author?.username }}</span>
            <span class="post-date">{{ formatDate(post.created_at) }}</span>
            <span class="post-views">조회 {{ post.views }}</span>
            <span class="post-likes">좋아요 {{ post.like_count || 0 }}</span>
            <span class="post-comments">댓글 {{ post.comment_count || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="pagination">
      <button 
        v-for="page in pageRange" 
        :key="page"
        @click="goToPage(page)"
        :class="{ 'active': currentPage === page }"
      >
        {{ page }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.js';
import axios from 'axios';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

const router = useRouter();
const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);

const posts = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const totalPosts = ref(0);
const selectedCategory = ref('');

const categories = [
  { value: '', label: '전체' },
  { value: 'notice', label: '공지사항' },
  { value: 'qna', label: 'Q&A' },
  { value: 'free', label: '자유게시판' },
];

const pageRange = computed(() => {
  const range = [];
  const maxVisiblePages = 5;
  let startPage = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2));
  let endPage = startPage + maxVisiblePages - 1;

  if (endPage > totalPages.value) {
    endPage = totalPages.value;
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    range.push(i);
  }
  return range;
});

const fetchPosts = async (page = 1) => {
  try {
    loading.value = true;
    const response = await axios.get('http://localhost:8000/articles/', {
      params: {
        page,
        category: selectedCategory.value || undefined,
      },
    });
    posts.value = response.data.results || [];
    totalPosts.value = response.data.count || 0;
    totalPages.value = Math.ceil(totalPosts.value / 10);
    currentPage.value = page;
  } catch (error) {
    console.error('게시글을 불러오는 중 오류가 발생했습니다:', error);
  } finally {
    loading.value = false;
  }
};

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return;
  fetchPosts(page);
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const filterByCategory = (category) => {
  selectedCategory.value = category;
  currentPage.value = 1;
  fetchPosts(1);
};

const goToPost = (postId) => {
  router.push(`/community/${postId}`);
};

const writePost = () => {
  router.push('/community/write');
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return format(new Date(dateString), 'yyyy.MM.dd', { locale: ko });
};

const getCategoryClass = (category) => category || '';

const getCategoryLabel = (category) => {
  const categoryMap = {
    'notice': '공지',
    'tip': '개발팁',
    'qna': 'Q&A',
    'free': '자유',
  };
  return categoryMap[category] || category;
};

onMounted(() => {
  fetchPosts(1);
});

watch(() => router.currentRoute.value.query, (newQuery) => {
  if (newQuery.page) {
    const page = parseInt(newQuery.page, 10);
    if (!isNaN(page) && page !== currentPage.value) {
      fetchPosts(page);
    }
  }
}, { immediate: true });
</script>

<style scoped>
.community-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: 80vh;
}

/* Page Header */
.page-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #333;
}

.page-header h1 {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 16px 0;
  color: #222;
}

.page-header-controls {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 정보는 왼쪽, 버튼은 오른쪽 */
}

.page-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #666;
  font-size: 15px;
}

.page-info strong {
  color: #1976d2;
}

.page-divider {
  color: #eee;
}

.write-button-top {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 18px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.write-button-top:hover {
  background-color: #1565c0;
}

/* Category Filter */
.category-filter {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.category-filter button {
  padding: 6px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.category-filter button.active {
  background-color: #1976d2;
  color: white;
  border-color: #1976d2;
}

/* Post List */
.post-list {
  margin-bottom: 40px;
}

.post-item {
  display: flex;
  padding: 20px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.post-item:hover {
  background-color: #f9f9f9;
}

.post-category {
  min-width: 70px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-right: 20px;
}

.post-category.notice { background-color: #e3f2fd; color: #1976d2; }
.post-category.qna { background-color: #fff3e0; color: #f57c00; }
.post-category.free { background-color: #f3e5f5; color: #8e24aa; }

.post-content { flex: 1; overflow: hidden; }

.post-title {
  font-size: 17px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #333;
}

.post-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}

.post-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #888;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.pagination button {
  min-width: 36px;
  height: 36px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button.active {
  background-color: #1976d2;
  color: white;
  border-color: #1976d2;
}

.loading, .no-posts {
  text-align: center;
  padding: 60px 0;
  color: #888;
}
</style>