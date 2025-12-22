<template>
  <div class="community-container">
    <!-- Page Header -->
    <div class="page-header">
      <h1>전체 게시판</h1>
      <div class="page-info">
        <span>총 {{ totalPosts }}개의 게시글</span>
        <span class="page-number">{{ currentPage }}/{{ totalPages }} 페이지</span>
      </div>
    </div>

    <!-- Category Filter -->
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

    <!-- Post List -->
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
        @click="goToPost(post.id)"
      >
        <div class="post-category" :class="getCategoryClass(post.category)">
          {{ getCategoryLabel(post.category) }}
        </div>
        <div class="post-content">
          <h3 class="post-title">{{ post.title }}</h3>
          <p class="post-desc">{{ post.content.substring(0, 100) }}{{ post.content.length > 100 ? '...' : '' }}</p>
          <div class="post-meta">
            <span class="post-author">{{ post.author.username }}</span>
            <span class="post-date">{{ formatDate(post.created_at) }}</span>
            <span class="post-views">조회 {{ post.views }}</span>
            <span class="post-likes">좋아요 {{ post.like_count || 0 }}</span>
            <span class="post-comments">댓글 {{ post.comment_count || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
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

    <!-- Write Post Button -->
    <button class="write-button" @click="writePost">
      <i class="fas fa-pen"></i>
      <span>글쓰기</span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

const router = useRouter();

// State
const posts = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const totalPosts = ref(0);
const selectedCategory = ref('');

// Constants
const categories = [
  { value: '', label: '전체' },
  { value: 'notice', label: '공지사항' },
  { value: 'qna', label: 'Q&A' },
  { value: 'free', label: '자유게시판' },
];

// Computed
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

// Methods
const fetchPosts = async (page = 1) => {
  try {
    loading.value = true;
    const response = await axios.get('http://localhost:8000/articles/', {  // Changed URL to point to Django backend
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
    alert('게시글을 불러오는 중 오류가 발생했습니다.');
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
  return format(new Date(dateString), 'yyyy.MM.dd', { locale: ko });
};

const getCategoryClass = (category) => {
  return category || '';
};

const getCategoryLabel = (category) => {
  const categoryMap = {
    'notice': '공지',
    'tip': '개발팁',
    'qna': 'Q&A',
    'free': '자유',
  };
  return categoryMap[category] || category;
};

// Lifecycle Hooks
onMounted(() => {
  fetchPosts(1);
});

// Watch for route changes
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
  position: relative;
  min-height: 80vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid #eee;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #666;
  font-size: 14px;
}

.page-number {
  font-weight: 500;
  color: #1976d2;
}

/* Category Filter */
.category-filter {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-wrap: wrap;
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

.category-filter button:hover {
  background-color: #f5f5f5;
}

.category-filter button.active {
  background-color: #1976d2;
  color: white;
  border-color: #1976d2;
}

/* Post List */
.post-list {
  margin-bottom: 40px;
  min-height: 300px;
}

.post-item {
  display: flex;
  padding: 20px 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.2s;
  cursor: pointer;
  border-radius: 8px;
  margin-bottom: 8px;
}

.post-item:hover {
  background-color: #f9f9f9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.post-category.notice {
  background-color: #e3f2fd;
  color: #1976d2;
}

.post-category.tip {
  background-color: #e8f5e9;
  color: #388e3c;
}

.post-category.qna {
  background-color: #fff3e0;
  color: #f57c00;
}

.post-category.free {
  background-color: #f3e5f5;
  color: #8e24aa;
}

.post-content {
  flex: 1;
  overflow: hidden;
}

.post-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #888;
  flex-wrap: wrap;
}

.post-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.post-meta i {
  font-size: 12px;
}

/* Loading State */
.loading,
.no-posts {
  text-align: center;
  padding: 60px 0;
  color: #888;
  font-size: 16px;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin: 40px 0;
  flex-wrap: wrap;
}

.pagination button {
  min-width: 36px;
  height: 36px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  font-size: 14px;
}

.pagination button:hover {
  background-color: #f5f5f5;
}

.pagination button.active {
  background-color: #1976d2;
  color: white;
  border-color: #1976d2;
  font-weight: 500;
}

/* Write Button */
.write-button {
  position: fixed;
  bottom: 40px;
  right: 40px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 30px;
  height: 50px;
  padding: 0 24px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  z-index: 100;
}

.write-button:hover {
  background-color: #1565c0;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 118, 210, 0.4);
}

.write-button i {
  font-size: 16px;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .post-item {
    flex-direction: column;
    gap: 12px;
    padding: 16px;
  }
  
  .post-category {
    align-self: flex-start;
    margin: 0;
  }
  
  .write-button {
    bottom: 20px;
    right: 20px;
    height: 50px;
    width: 50px;
    border-radius: 50%;
    padding: 0;
  }
  
  .write-button span {
    display: none;
  }
  
  .write-button i {
    font-size: 18px;
  }
}
</style>

<style scoped>
/* 기존 main.css 최대 활용 → 최소 보정만 */
.list-desc {
  padding-left: 16px;
}

.list-desc li {
  list-style: disc;
}

.detail-desc li {
  margin-bottom: 6px;
}
</style>
