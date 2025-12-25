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
            <option value="notice">공지</option>
            <option value="qna">Q&A</option>
            <option value="estimate">견적 요청</option>
            <option value="free">자유게시판</option>
          </select>
        </div>
      </div>

      <div v-if="category === 'estimate'" class="form-group">
        <label>비교/문의할 노트북 선택 <span class="required">*</span></label>
        <p class="help-text">위시리스트의 제품 중 상담받고 싶은 모델을 선택하세요.</p>
        
        <div v-if="selectedLaptops.length > 0" class="selected-laptop-cards">
          <div v-for="laptop in selectedLaptops" :key="laptop.id" class="selected-card">
            <div class="card-mini-img">
              <img :src="getItemImage(laptop)" alt="">
            </div>
            <div class="card-mini-info">
              <span class="card-mini-name">{{ laptop.name || laptop.title || '제품명 없음' }}</span>
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
            <p>위시리스트가 비어있습니다. 상품을 먼저 찜해주세요!</p>
          </div>
        </div>
      </div>
      
      <div v-if="category === 'estimate'" class="form-group estimate-note">
        <div class="info-box">
          <i class="fas fa-comment-dots"></i>
          <div>
            <strong>어떤 점이 궁금하신가요?</strong>
            <ul class="example-list">
              <li>"이 사양으로 프리미어 프로 컷 편집 원활할까요?"</li>
              <li>"대학생 과제용으로 무게와 성능 중 뭐가 나을까요?"</li>
              <li>"지금 가격이 적당한지 궁금합니다."</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="title">제목</label>
        <input id="title" v-model="title" type="text" placeholder="제목을 입력하세요" required />
      </div>

      <div class="form-group">
        <label for="content">내용 <span class="required">*</span></label>
        <textarea
          id="content"
          v-model="content"
          :placeholder="category === 'estimate' ? '선택한 노트북들에 대해 궁금한 점을 자세히 적어주시면 정확한 답변을 받을 수 있습니다.' : '내용을 작성해 주세요.'"
          rows="10"
          required
        ></textarea>
      </div>

      <div class="form-actions">
        <button type="button" class="btn-cancel" @click="router.back()">취소</button>
        <button type="submit" class="btn-submit">게시글 등록</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const title = ref('');
const content = ref('');
const category = ref('free');
const selectedLaptopIds = ref([]);
const selectedLaptops = ref([]);
const wishlist = ref([]);

const isLaptopSelected = (laptopId) => selectedLaptopIds.value.includes(laptopId);

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

onMounted(() => {
  const savedWishlist = localStorage.getItem('wishlist');
  if (savedWishlist) {
    wishlist.value = JSON.parse(savedWishlist);
  }
});

const formatPrice = (price) => price ? price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '0';
const getItemImage = (item) => {
  if (!item) return 'https://via.placeholder.com/100';
  return item.image || item.imageUrl || 'https://via.placeholder.com/100';
};

const submitPost = async () => {
  // (기존 제출 로직과 동일)
  try {
    if (!title.value.trim() || !content.value.trim()) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    const userData = localStorage.getItem('user');
    const token = userData ? JSON.parse(userData)?.access : null;
    if (!token) { alert('로그인이 필요합니다.'); router.push('/login'); return; }

    if (category.value === 'estimate' && selectedLaptopIds.value.length === 0) {
      alert('최소 한 개의 제품을 선택해주세요.');
      return;
    }

    const requestData = {
      title: title.value,
      content: content.value,
      category: category.value,
      ...(category.value === 'estimate' && { laptops: selectedLaptopIds.value })
    };

    const response = await axios.post('http://localhost:8000/articles/', requestData, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });

    if (response.status === 201) {
      alert('등록되었습니다.');
      router.push('/community');
    }
  } catch (error) {
    console.error(error);
    alert('등록 중 오류가 발생했습니다.');
  }
};
</script>

<style scoped>
.write-container { max-width: 850px; margin: 40px auto; padding: 0 20px; font-family: 'Pretendard', sans-serif; }
.write-header { margin-bottom: 30px; text-align: left; }
.write-header h1 { font-size: 26px; color: #2f3a45; font-weight: 700; }
.write-form { background: #fff; padding: 32px; border-radius: 16px; border: 1px solid #eef0f2; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }

/* 견적 선택 영역 스타일 수정 */
.laptop-selection-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin-top: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
  border: 1px solid #e0e4e8;
  border-radius: 12px;
  background: #fcfdfe;
}

.laptop-select-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
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
  border-color: #cbd5e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.laptop-select-item.is-active {
  border-color: #3182ce;
  background-color: #f7fafc;
}

.select-item-header { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.item-name { flex: 1; font-weight: 700; color: #333; font-size: 15px; }
.item-price { color: #1976d2; font-weight: 800; font-size: 14px; }

.item-spec-preview {
  font-size: 12px;
  color: #778;
  padding-left: 28px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 체크박스 커스텀 */
.custom-check {
  width: 18px; height: 18px;
  border: 2px solid #ccc;
  border-radius: 4px;
  position: relative;
}
.custom-check.checked { background: #1976d2; border-color: #1976d2; }
.custom-check.checked::after {
  content: '✓'; color: #fff; font-size: 12px;
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
}

/* 선택된 노트북 카드 레이아웃 */
.selected-laptop-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.selected-card {
  display: flex;
  align-items: center;
  background: #f8fbff;
  border: 1px solid #d0e3ff;
  border-radius: 10px;
  padding: 12px;
  position: relative;
}

.card-mini-img { width: 60px; height: 40px; margin-right: 15px; }
.card-mini-img img { width: 100%; height: 100%; object-fit: contain; }
.card-mini-name { display: block; font-weight: 700; font-size: 14px; margin-bottom: 4px; color: #2f3a45; }
.card-mini-specs { display: flex; flex-wrap: wrap; gap: 4px; }
.mini-spec-tag { font-size: 10px; background: #fff; border: 1px solid #d0e3ff; padding: 1px 6px; border-radius: 4px; color: #666; }

.card-remove-btn {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  background: none; border: none; color: #ff4d4f; cursor: pointer; font-size: 18px;
}

/* 공통 폼 스타일 */
.form-group { margin-bottom: 24px; }
.form-group label { display: block; font-weight: 700; margin-bottom: 10px; color: #2f3a45; }
.required { color: #ff4d4f; }
.help-text { font-size: 13px; color: #889; margin-top: -5px; margin-bottom: 12px; }

input[type="text"], textarea, select {
  width: 100%; padding: 14px; border: 1px solid #ddd; border-radius: 10px;
  background: #fcfcfc; transition: 0.2s;
}
input:focus, textarea:focus { border-color: #1976d2; background: #fff; outline: none; box-shadow: 0 0 0 4px rgba(25,118,210,0.05); }

.estimate-note { background: #f4f7fa; padding: 20px; border-radius: 12px; }
.info-box { display: flex; gap: 12px; }
.info-box i { color: #1976d2; font-size: 20px; }
.example-list { margin-top: 10px; padding-left: 20px; font-size: 13px; color: #556; }

.form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 40px; }
.btn-cancel { padding: 14px 28px; background: #eee; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-submit { padding: 14px 40px; background: #2f3a45; color: #fff; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-submit:hover { background: #1976d2; }

.empty-wishlist-note { padding: 40px; text-align: center; color: #adb5bd; }
.empty-wishlist-note i { font-size: 30px; margin-bottom: 10px; }
</style>