<template>
  <div class="community-page">
    <div class="community-container">
      <header class="page-header">
        <div class="header-content">
          <div class="header-text">
            <h1 class="title">커뮤니티 <span>Space</span></h1>
            <p class="subtitle">Mr.PC Picker 사용자들과 함께 스마트한 IT 생활을 공유하세요.</p>
          </div>
          <button 
            v-if="isAuthenticated" 
            class="write-floating-btn" 
            @click="writePost"
          >
            <i class="fas fa-pen"></i> 게시글 작성
          </button>
        </div>

        <div class="stats-overview">
          <div class="stat-box">
            <span class="label">총 게시글</span>
            <span class="value">{{ totalPosts }}</span>
          </div>
          <div class="stat-box">
            <span class="label">현재 페이지</span>
            <span class="value">{{ currentPage }} / {{ totalPages }}</span>
          </div>
        </div>
      </header>

      <div class="filter-wrapper">
        <nav class="category-tabs">
          <button 
            v-for="category in categories" 
            :key="category.value"
            :class="{ 'active': selectedCategory === category.value }"
            @click="filterByCategory(category.value)"
          >
            {{ category.label }}
          </button>
        </nav>
      </div>

      <div class="post-list-wrapper">
        <div v-if="loading" class="state-container">
          <div class="custom-loader"></div>
          <p>정보를 불러오는 중입니다...</p>
        </div>
        
        <div v-else-if="posts.length === 0" class="state-container no-posts">
          <div class="empty-icon">📂</div>
          <p>아직 작성된 글이 없습니다. 첫 주인공이 되어보세요!</p>
        </div>

        <div v-else class="post-grid">
          <div 
            v-for="post in posts" 
            :key="post.id" 
            class="premium-post-card"
            :class="{ 'featured': post.category === 'notice' }"
            @click="goToPost(post.id)"
          >
            <div class="card-top">
              <span class="category-badge" :class="post.category">
                {{ getCategoryLabel(post.category) }}
              </span>
              <span class="time-stamp">{{ formatDate(post.created_at) }}</span>
            </div>
            
            <div class="card-body">
              <h3 class="post-title">{{ post.title }}</h3>
              <p class="post-preview">{{ truncateContent(post.content) }}</p>
            </div>
            
            <div class="card-bottom">
              <div class="user-info">
                <div class="avatar">{{ post.author?.username?.charAt(0) || 'U' }}</div>
                <span class="username">{{ post.author?.username || '익명' }}</span>
              </div>
              <div class="post-counters">
                <div class="count-item" title="조회수">
                  <i class="far fa-eye"></i> {{ post.views || 0 }}
                </div>
                <div class="count-item liked" title="추천">
                  <i class="far fa-heart"></i> {{ post.like_count || 0 }}
                </div>
                <div class="count-item commented" title="댓글">
                  <i class="far fa-comment-dots"></i> {{ post.comment_count || 0 }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <nav class="modern-pagination" v-if="totalPages > 1">
        <button 
          class="nav-arrow" 
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <div class="pages">
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
          class="nav-arrow" 
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          <i class="fas fa-chevron-right"></i>
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

// 상태 관리
const isAuthenticated = ref(!!AuthService.getCurrentUser());
const posts = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const totalPosts = ref(0);
const selectedCategory = ref('all');

// 카테고리 정의
const categories = [
  { value: 'all', label: '전체' },
  { value: 'notice', label: '공지사항' },
  { value: 'qna', label: 'Q&A' },
  { value: 'estimate', label: '견적질문' },
  { value: 'free', label: '자유게시판' },
];

// 페이지네이션 범위 계산
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
    if (i > 0) range.push(i);
  }
  return range;
});

// 게시글 데이터 가져오기
const fetchPosts = async (page = 1) => {
  try {
    loading.value = true;
    const params = {
      page,
      category: selectedCategory.value === 'all' ? '' : selectedCategory.value,
    };

    const response = await axios.get('http://localhost:8000/articles/', { params });
    
    // API 응답 구조에 맞게 데이터 할당
    posts.value = response.data.results || [];
    totalPosts.value = response.data.count || 0;
    // 장고 기본 페이징(10개씩) 기준 페이지 수 계산
    totalPages.value = Math.ceil(totalPosts.value / 10) || 1;
    currentPage.value = page;

  } catch (error) {
    console.error('Error fetching posts:', error);
    // API 에러 발생 시 초기화
    posts.value = [];
    totalPosts.value = 0;
    totalPages.value = 1;
  } finally {
    loading.value = false;
  }
};

// 이벤트 핸들러
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

// 포맷팅 함수
const formatDate = (dateString) => {
  if (!dateString) return '';
  return format(new Date(dateString), 'yyyy.MM.dd', { locale: ko });
};

const truncateContent = (content) => {
  if (!content) return '';
  return content.length > 150 ? content.substring(0, 150) + '...' : content;
};

const getCategoryLabel = (category) => {
  const categoryMap = {
    'notice': '공지사항',
    'qna': 'Q&A',
    'estimate': '견적질문',
    'free': '자유게시판',
  };
  return categoryMap[category] || '자유게시판';
};

onMounted(() => {
  fetchPosts(1);
});
</script>

<style scoped>
/* 이전 스타일 코드 동일 */
.community-page {
  background-color: #fcfdfe;
  min-height: 100vh;
  padding: 60px 20px;
  font-family: 'Pretendard', -apple-system, sans-serif;
  color: #334155;
}

.community-container {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 40px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 30px;
}

.title {
  font-size: 38px;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 10px 0;
  letter-spacing: -1px;
}

.title span {
  color: #3b82f6;
}

.subtitle {
  color: #64748b;
  font-size: 17px;
  margin: 0;
}

.write-floating-btn {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 14px;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(30, 41, 59, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
}

.write-floating-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(30, 41, 59, 0.3);
  background: #3b82f6;
}

.stats-overview {
  display: flex;
  gap: 20px;
}

.stat-box {
  background: white;
  padding: 12px 20px;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
}

.stat-box .label { font-size: 12px; color: #94a3b8; font-weight: 600; }
.stat-box .value { font-size: 18px; color: #1e293b; font-weight: 700; }

.filter-wrapper {
  margin-bottom: 30px;
  border-bottom: 2px solid #f1f5f9;
}

.category-tabs {
  display: flex;
  gap: 5px;
}

.category-tabs button {
  padding: 12px 24px;
  border: none;
  background: none;
  font-size: 15px;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}

.category-tabs button:hover { color: #1e293b; }

.category-tabs button.active {
  color: #3b82f6;
}

.category-tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #3b82f6;
}

.post-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.premium-post-card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  border: 1px solid #f1f5f9;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.premium-post-card:hover {
  border-color: #3b82f6;
  transform: scale(1.01);
  box-shadow: 0 10px 30px rgba(59, 130, 246, 0.08);
}

.premium-post-card.featured {
  background: #f8faff;
  border-left: 4px solid #3b82f6;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.category-badge {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
}

.category-badge.notice { background: #fee2e2; color: #ef4444; }
.category-badge.qna { background: #dcfce7; color: #22c55e; }
.category-badge.estimate { background: #eff6ff; color: #3b82f6; }
.category-badge.free { background: #f1f5f9; color: #64748b; }

.time-stamp { font-size: 13px; color: #94a3b8; }

.post-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 10px 0;
}

.post-preview {
  font-size: 15px;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 24px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #f8fafc;
}

.user-info { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 32px; height: 32px; background: #e2e8f0; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #64748b; font-size: 12px;
}
.username { font-size: 14px; font-weight: 600; color: #334155; }

.post-counters { display: flex; gap: 18px; }
.count-item { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #94a3b8; font-weight: 600; }
.count-item.liked i { color: #f43f5e; }
.count-item.commented i { color: #3b82f6; }

.modern-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 50px;
}

.pages { display: flex; gap: 8px; }
.pages button, .nav-arrow {
  width: 44px; height: 44px; border-radius: 12px;
  border: 1px solid #e2e8f0; background: white;
  color: #64748b; font-weight: 700; cursor: pointer;
  transition: all 0.2s;
}

.pages button.active {
  background: #3b82f6; color: white; border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.state-container { text-align: center; padding: 100px 0; color: #94a3b8; }
.custom-loader {
  width: 40px; height: 40px; border: 4px solid #f1f5f9;
  border-top-color: #3b82f6; border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>