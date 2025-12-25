<template>
  <div class="write-container">
    <div class="write-header">
      <h1>게시글 수정</h1>
      <p>작성하신 내용을 수정하고 업데이트하세요.</p>
    </div>

    <form class="write-form" @submit.prevent="updatePost">
      <div class="form-group">
        <label for="category">카테고리</label>
        <div class="select-wrapper">
          <select id="category" v-model="post.category" disabled>
            <option value="notice">공지</option>
            <option value="qna">Q&A</option>
            <option value="estimate">견적 요청</option>
            <option value="free">자유게시판</option>
          </select>
        </div>
      </div>

      <div v-if="post.category === 'estimate'" class="form-group">
        <label>비교/문의할 노트북 선택 <span class="required">*</span></label>
        <p class="help-text">위시리스트의 제품 중 상담받고 싶은 모델을 선택하세요.</p>
        
        <div v-if="selectedLaptops.length > 0" class="selected-laptop-cards">
          <div v-for="laptop in selectedLaptops" :key="laptop.id" class="selected-card">
            <div class="card-mini-img">
              <img :src="getItemImage(laptop)" alt="laptop">
            </div>
            <div class="card-mini-info">
              <span class="card-mini-name">{{ laptop.name || laptop.title || `PC ${laptop.id}` }}</span>
              <div class="card-mini-specs">
                <span v-for="spec in laptop.specs" :key="spec" class="mini-spec-tag">{{ spec }}</span>
              </div>
            </div>
            <button type="button" @click="removeLaptop(laptop.id)" class="card-remove-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <div class="laptop-selection-grid">
          <div 
            v-for="laptop in wishlist" 
            :key="laptop.id" 
            class="laptop-select-item"
            :class="{ 'is-active': isLaptopSelected(laptop.id) }"
            @click="toggleLaptopSelection(laptop)"
          >
            <div class="select-item-image">
              <img :src="getItemImage(laptop)" :alt="laptop.name || laptop.title" class="laptop-thumbnail">
            </div>
            <div class="select-item-content">
              <div class="select-item-header">
                <div class="custom-check" :class="{ 'checked': isLaptopSelected(laptop.id) }"></div>
                <span class="item-name">{{ laptop.name || laptop.title || '제품명 없음' }}</span>
                <span class="item-price">₩{{ formatPrice(laptop.price) }}</span>
              </div>
              <div class="item-spec-preview">
                {{ laptop.specs?.join(' / ') || '상세 정보 없음' }}
              </div>
            </div>
          </div>
          
          <div v-if="wishlist.length === 0" class="empty-wishlist-note">
            <i class="fas fa-heart-broken"></i>
            <p>위시리스트가 비어있습니다.</p>
          </div>
        </div>
      </div>
      
      <div v-if="post.category === 'estimate'" class="form-group estimate-note">
        <div class="info-box">
          <i class="fas fa-comment-dots"></i>
          <div>
            <strong>궁금한 점을 구체적으로 수정해보세요!</strong>
            <ul class="example-list">
              <li>"영상 편집용으로 이 두 모델 중 가성비가 더 좋은 건 무엇인가요?"</li>
              <li>"실제 체감되는 배터리 타임이 궁금합니다."</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="title">제목</label>
        <input id="title" v-model="post.title" type="text" placeholder="제목을 입력하세요" required />
      </div>

      <div class="form-group">
        <label for="content">내용 <span class="required">*</span></label>
        <textarea
          id="content"
          v-model="post.content"
          rows="12"
          required
        ></textarea>
      </div>

      <div class="form-actions">
        <button type="button" class="btn-cancel" @click="router.back()">취소</button>
        <button type="submit" class="btn-submit">수정 완료</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const postId = route.params.id;

const post = ref({ title: '', content: '', category: '', laptops: [] });
const wishlist = ref([]);
const selectedLaptopIds = ref([]);
const selectedLaptops = ref([]);

// 헬퍼 함수
const formatPrice = (price) => price ? price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '0';
const getItemImage = (item) => {
  if (!item) return 'https://via.placeholder.com/100';
  const imageUrl = item.imageUrl || item.image;
  if (typeof imageUrl === 'object' && imageUrl !== null) {
    return imageUrl.url || 'https://via.placeholder.com/100';
  }
  return imageUrl || 'https://via.placeholder.com/100';
};
const isLaptopSelected = (laptopId) => selectedLaptopIds.value.includes(laptopId);

// 노트북 선택 로직
const toggleLaptopSelection = (laptop) => {
  const index = selectedLaptopIds.value.indexOf(laptop.id);
  if (index === -1) {
    selectedLaptopIds.value.push(laptop.id);
    selectedLaptops.value.push(laptop);
  } else {
    selectedLaptopIds.value.splice(index, 1);
    selectedLaptops.value = selectedLaptops.value.filter(l => l.id !== laptop.id);
  }
};

const removeLaptop = (laptopId) => {
  selectedLaptopIds.value = selectedLaptopIds.value.filter(id => id !== laptopId);
  selectedLaptops.value = selectedLaptops.value.filter(l => l.id !== laptopId);
};

// 데이터 로드
const fetchPost = async () => {
  try {
    const token = authStore.user?.access;
    if (!token) {
      alert('로그인이 필요합니다.');
      router.push('/login');
      return;
    }

    const response = await axios.get(`http://localhost:8000/articles/${postId}/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = response.data;
    
    // 권한 검사
    const authorId = typeof data.author === 'object' ? (data.author.id || data.author.pk) : data.author;
    const currentUserId = authStore.user?.user_id || authStore.user?.id || authStore.user?.pk;

    if (authorId && currentUserId && String(authorId) !== String(currentUserId)) {
      alert('본인만 수정 가능합니다.');
      router.back();
      return;
    }

    // 데이터 할당
    post.value = {
      title: data.title,
      content: data.content,
      category: data.category,
      laptops: data.laptops || []
    };

    // 기존 선택된 노트북 ID와 객체 매칭 (위시리스트 데이터 로드 후 진행)
    const savedWishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    wishlist.value = savedWishlist;
    
    // 서버에서 온 노트북 데이터를 현재 UI 상태로 동기화
    if (post.value.category === 'estimate') {
      const ids = post.value.laptops.map(l => (typeof l === 'object' ? l.id : l));
      selectedLaptopIds.value = ids;
      
      // Find laptops in wishlist first
      const laptopsFromWishlist = wishlist.value.filter(item => ids.includes(item.id));
      
      // If any laptops are missing from wishlist, try to get them from the post data
      if (laptopsFromWishlist.length < ids.length) {
        const missingIds = ids.filter(id => !laptopsFromWishlist.some(l => l.id === id));
        const laptopsFromPost = post.value.laptops
          .filter(l => {
            const laptopId = typeof l === 'object' ? l.id : l;
            return missingIds.includes(laptopId) && typeof l === 'object';
          })
          .map(l => ({
            id: l.id,
            name: l.name || l.title || `PC ${l.id}`,
            price: l.price || 0,
            specs: l.specs || [],
            image: l.image || l.imageUrl
          }));
        
        selectedLaptops.value = [...laptopsFromWishlist, ...laptopsFromPost];
      } else {
        selectedLaptops.value = laptopsFromWishlist;
      }
    }

  } catch (error) {
    console.error('Fetch Error:', error);
    alert('오류가 발생했습니다.');
    router.back();
  }
};

const updatePost = async () => {
  if (post.value.category === 'estimate' && selectedLaptopIds.value.length === 0) {
    alert('최소 한 개의 제품을 선택해주세요.');
    return;
  }

  const token = authStore.user?.access;
  try {
    const payload = {
      title: post.value.title,
      content: post.value.content,
      category: post.value.category,
      laptops: selectedLaptopIds.value // ID 리스트 전송
    };

    await axios.put(`http://localhost:8000/articles/${postId}/`, payload, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    alert('수정되었습니다.');
    router.push(`/community/${postId}`);
  } catch (error) {
    alert('수정 중 오류가 발생했습니다.');
  }
};

onMounted(fetchPost);
</script>

<style scoped>
/* 작성 페이지와 100% 동일한 스타일 적용 */
.write-container { max-width: 850px; margin: 40px auto; padding: 0 20px; font-family: 'Pretendard', sans-serif; }
.write-header { margin-bottom: 30px; }
.write-header h1 { font-size: 26px; color: #2f3a45; font-weight: 700; }
.write-form { background: #fff; padding: 32px; border-radius: 16px; border: 1px solid #eef0f2; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }

.laptop-selection-grid { border: 1px solid #e0e4e8; border-radius: 12px; max-height: 250px; overflow-y: auto; background: #fcfdfe; }
.laptop-select-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #f0f2f4;
  cursor: pointer;
  transition: 0.2s;
}

.select-item-image {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 6px;
  overflow: hidden;
}

.laptop-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 4px;
}

.select-item-content {
  flex: 1;
  min-width: 0;
}

.laptop-select-item:hover { 
  background: #f1f7ff; 
}

.laptop-select-item.is-active { 
  background: #f0f6ff; 
}

.select-item-header { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.item-name { flex: 1; font-weight: 700; color: #333; font-size: 14px; }
.item-price { color: #1976d2; font-weight: 800; font-size: 13px; }
.item-spec-preview { font-size: 12px; color: #778; padding-left: 28px; }

.custom-check { width: 18px; height: 18px; border: 2px solid #ccc; border-radius: 4px; position: relative; }
.custom-check.checked { background: #1976d2; border-color: #1976d2; }
.custom-check.checked::after { content: '✓'; color: #fff; font-size: 12px; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }

.selected-laptop-cards { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
.selected-card { display: flex; align-items: center; background: #f8fbff; border: 1px solid #d0e3ff; border-radius: 10px; padding: 12px; position: relative; }
.card-mini-img { width: 60px; height: 40px; margin-right: 15px; }
.card-mini-img img { width: 100%; height: 100%; object-fit: contain; }
.card-mini-name { display: block; font-weight: 700; font-size: 14px; margin-bottom: 4px; }
.card-mini-specs { display: flex; flex-wrap: wrap; gap: 4px; }
.mini-spec-tag { font-size: 10px; background: #fff; border: 1px solid #d0e3ff; padding: 1px 6px; border-radius: 4px; color: #666; }
.card-remove-btn { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #ff4d4f; cursor: pointer; font-size: 18px; }

.form-group { margin-bottom: 24px; }
.form-group label { display: block; font-weight: 700; margin-bottom: 10px; }
.help-text { font-size: 13px; color: #889; margin-bottom: 12px; }
input[type="text"], textarea, select { width: 100%; padding: 14px; border: 1px solid #ddd; border-radius: 10px; background: #fcfcfc; }

.estimate-note { background: #f4f7fa; padding: 20px; border-radius: 12px; }
.info-box { display: flex; gap: 12px; }
.info-box i { color: #1976d2; font-size: 20px; }
.example-list { margin-top: 8px; padding-left: 18px; font-size: 13px; color: #556; }

.form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 40px; }
.btn-cancel { padding: 14px 28px; background: #eee; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-submit { padding: 14px 40px; background: #2f3a45; color: #fff; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; }
</style>