<template>
  <div class="community-page">
    <div class="community-container">
      <header class="page-header">
        <div class="header-text">
          <h1 class="title">커뮤니티</h1>
          <p class="subtitle">Mr.PC Picker 사용자들과 정보를 공유하세요.</p>
        </div>
        
        <div class="page-header-controls">
          <div class="page-info">
            <span>총 <strong>{{ totalPosts }}</strong>개의 게시글</span>
            <span class="page-divider"></span>
            <span class="page-number">{{ currentPage }} / {{ totalPages }} 페이지</span>
          </div>
          <button 
            v-if="isAuthenticated" 
            class="write-btn" 
            @click="writePost"
          >
            <i class="fas fa-edit"></i> 글쓰기
          </button>
        </div>
      </header>

      <nav class="category-filter">
        <button 
          v-for="category in categories" 
          :key="category.value"
          :class="{ 'active': selectedCategory === category.value }"
          @click="filterByCategory(category.value)"
        >
          {{ category.label }}
        </button>
      </nav>

      <div class="post-list">
        <div v-if="loading" class="state-message">
          <div class="loader"></div>
          <p>게시글을 불러오고 있습니다...</p>
        </div>
        
        <div v-else-if="posts.length === 0" class="state-message no-posts">
          <i class="fas fa-folder-open"></i>
          <p>등록된 게시글이 없습니다.</p>
        </div>

        <div 
          v-else
          v-for="post in posts" 
          :key="post.id" 
          class="post-card"
          @click="goToPost(post.id)"
        >
          <div class="post-card-header">
            <span class="post-category" :class="getCategoryClass(post.category)">
              {{ getCategoryLabel(post.category) }}
            </span>
            <h3 class="post-title">{{ post.title }}</h3>
          </div>
          
          <p class="post-excerpt">
            {{ post.content.substring(0, 120) }}{{ post.content.length > 120 ? '...' : '' }}
          </p>
          
          <div class="post-card-footer">
            <div class="post-author-info">
              <span class="author-name">{{ post.author?.username || '익명' }}</span>
              <span class="dot">·</span>
              <span class="post-date">{{ formatDate(post.created_at) }}</span>
            </div>
            
            <div class="post-stats">
              <span class="stat-item">
                <i class="far fa-eye"></i>
                <span class="stat-label">조회수</span>
                <span class="stat-value">{{ post.views }}</span>
              </span>
              <span class="stat-item">
                <i class="far fa-thumbs-up"></i>
                <span class="stat-label">좋아요</span>
                <span class="stat-value">{{ post.like_count || 0 }}</span>
              </span>
              <span class="stat-item">
                <i class="far fa-comment"></i>
                <span class="stat-label">댓글</span>
                <span class="stat-value">{{ post.comment_count || 0 }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <nav class="pagination-container">
        <button 
          class="page-nav-btn" 
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          &lt;
        </button>
        
        <div class="page-numbers">
          <button 
            v-for="page in pageRange" 
            :key="page"
            @click="goToPage(page)"
            :class="{ 'active': currentPage === page }"
          >
            {{ page }}
          </button>
        </div>

        <button 
          class="page-nav-btn" 
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          &gt;
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import AuthService from '@/services/AuthService'; 
import axios from 'axios';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

const router = useRouter();
const isAuthenticated = ref(!!AuthService.getCurrentUser());

const posts = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const totalPosts = ref(0);
const selectedCategory = ref('');

const categories = [
  { value: 'all', label: '전체' },
  { value: 'notice', label: '공지사항' },
  { value: 'qna', label: 'Q&A' },
  { value: 'estimate', label: '견적질문' },
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
    // Try to fetch from API first
    try {
      const response = await axios.get('http://localhost:8000/articles/', {
        params: {
          page,
          category: selectedCategory.value === 'all' ? '' : selectedCategory.value,
        },
      });
      posts.value = response.data.results || [];
      totalPosts.value = response.data.count || 0;
      totalPages.value = Math.ceil(totalPosts.value / 10) || 1;
      currentPage.value = page;
    } catch (apiError) {
      console.warn('API fetch failed, falling back to localStorage', apiError);
      
      // Fallback to localStorage
      const savedPosts = JSON.parse(localStorage.getItem('communityPosts') || '[]');
      
      // Filter by category if selected
      let filteredPosts = [...savedPosts];
      if (selectedCategory.value && selectedCategory.value !== 'all') {
        filteredPosts = savedPosts.filter(post => post.type === selectedCategory.value);
      }
      
      // Simple pagination for localStorage
      const itemsPerPage = 10;
      const startIndex = (page - 1) * itemsPerPage;
      const endIndex = startIndex + itemsPerPage;
      
      posts.value = filteredPosts.slice(startIndex, endIndex);
      totalPosts.value = filteredPosts.length;
      totalPages.value = Math.ceil(filteredPosts.length / itemsPerPage) || 1;
      currentPage.value = page;
    }
  } catch (error) {
    console.error('Error fetching posts:', error);
    posts.value = [];
    totalPosts.value = 0;
    totalPages.value = 1;
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
  router.push({ name: 'write-post' });
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return format(new Date(dateString), 'yyyy.MM.dd', { locale: ko });
};

const getCategoryClass = (category) => category === 'estimate' ? 'qna' : (category || 'free');

const getCategoryLabel = (category) => {
  const categoryMap = {
    'notice': '공지',
    'qna': '질문',
    'estimate': '견적',
    'free': '자유',
    'tip': '팁',
  };
  return categoryMap[category] || '자유';
};

onMounted(() => {
  fetchPosts(1);
});
</script>

<style scoped>
.community-page {
  background-color: #f8f9fa;
  min-height: 100vh;
  padding: 40px 20px 80px;
  font-family: system-ui, -apple-system, sans-serif;
}

.community-container {
  max-width: 900px;
  margin: 0 auto;
}

/* Header */
.page-header {
  margin-bottom: 32px;
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: #2f3a45;
  margin-bottom: 8px;
}

.subtitle {
  color: #6c757d;
  font-size: 16px;
  margin-bottom: 24px;
}

.page-header-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

.page-info {
  font-size: 14px;
  color: #6c757d;
}

.page-info strong {
  color: #1e6fd7;
}

.page-divider {
  display: inline-block;
  width: 1px;
  height: 12px;
  background: #dee2e6;
  margin: 0 12px;
}

.write-btn {
  background-color: #2f3a45;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.write-btn:hover {
  background-color: #1e6fd7;
  transform: translateY(-1px);
}

/* Category Filter */
.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
  flex-wrap: wrap;
  gap: 15px;
}

.category-filter {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.category-filter button {
  padding: 8px 18px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 500;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s;
}

.category-filter button:hover {
  border-color: #2f3a45;
  color: #2f3a45;
}

.category-filter button.active {
  background-color: #2f3a45;
  color: white;
  border-color: #2f3a45;
}

/* Post Cards */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 40px;
}

.post-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.03);
  border: 1px solid #f1f3f5;
  cursor: pointer;
  transition: all 0.2s;
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
  border-color: #1e6fd7;
}

.post-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.post-category {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 800;
}

.post-category.notice { background: #fff0f0; color: #e03131; }
.post-category.qna { background: #e7f5ff; color: #1e6fd7; }
.post-category.free { background: #f8f9fa; color: #495057; }

.post-title {
  font-size: 18px;
  font-weight: 700;
  color: #2f3a45;
  margin: 0;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-excerpt {
  font-size: 14px;
  color: #6c757d;
  line-height: 1.6;
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
  text-overflow: ellipsis;
  max-height: 3.2em;
}

.post-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f8f9fa;
}

.post-author-info {
  font-size: 13px;
  color: #868e96;
}

.author-name {
  font-weight: 600;
  color: #495057;
}

.dot { margin: 0 8px; }

/* Stat Items */
.post-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #868e96;
}

.stat-label {
  font-weight: 500;
  color: #adb5bd;
}

.stat-value {
  font-weight: 600;
  color: #495057;
}

.stat-item i {
  font-size: 14px;
  color: #dee2e6;
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.page-numbers {
  display: flex;
  gap: 8px;
}

.page-numbers button, .page-nav-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  background: white;
  color: #495057;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.page-numbers button.active {
  background-color: #1e6fd7;
  color: white;
  border-color: #1e6fd7;
}

.page-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* States */
.state-message {
  text-align: center;
  padding: 80px 0;
}

.loader {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1e6fd7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 600px) {
  .page-header-controls {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  .stat-label {
    display: none; /* 모바일에선 글자 숨김 */
  }
}
</style>