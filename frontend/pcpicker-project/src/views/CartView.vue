<template>
  <div class="wishlist-page">
    <header class="wishlist-hero">
      <div class="hero-inner">
        <div class="hero-text">
          <h1 class="hero-title">
            WISHLIST
          </h1>
          <p class="hero-desc">
            관심 있는 제품을 한눈에 비교하고 관리하세요.<br />
            나만의 구성을 완성하기 위한 최적의 아이템들입니다.
          </p>
        </div>

        <div class="hero-actions">
          <div class="modern-select-wrapper">
            <select v-model="sortOption" @change="sortItems" class="modern-select">
              <option value="recent">LATEST</option>
              <option value="price_asc">LOW PRICE</option>
              <option value="price_desc">HIGH PRICE</option>
            </select>
          </div>
        </div>
      </div>
    </header>

    <main class="main-container">
      <div v-if="cartItems.length === 0" class="empty-wishlist">
        <div class="empty-symbol">!</div>
        <h2>찜한 상품이 없습니다</h2>
        <p>나만의 구성을 위한 아이템을 찾아보세요.</p>
        <router-link to="/community" class="browse-btn">COLLECTION EXPLORE</router-link>
      </div>

      <div v-else class="wishlist-content">
        <div class="control-bar">
          <label class="modern-checkbox-container">
            <input type="checkbox" v-model="selectAll">
            <span class="checkmark"></span>
            <span class="label-txt">SELECT ALL ({{ selectedItems.length }}/{{ cartItems.length }})</span>
          </label>
          
          <button 
            v-show="selectedItems.length > 0" 
            @click="removeSelected" 
            class="btn-action-delete"
          >
            선택 삭제
          </button>
        </div>

        <div class="wishlist-grid">
          <div 
            v-for="item in cartItems" 
            :key="item.id" 
            class="wishlist-card"
            :class="{ 'is-selected': isSelected(item.id) }"
          >
            <label class="card-check-overlay">
              <input 
                type="checkbox" 
                :value="item.id"
                v-model="selectedItems"
              >
              <span class="checkmark"></span>
            </label>
            
            <div class="card-image-box">
              <img :src="getItemImage(item)" :alt="item.name" class="card-image">
            </div>

            <div class="card-body">
              <h3 class="item-name">{{ item.name }}</h3>
              
              <div v-if="item.specs && item.specs.length > 0" class="item-specs">
                <span v-for="(spec, specIndex) in item.specs" :key="specIndex" class="spec-tag">
                  {{ spec }}
                </span>
              </div>
              
              <div class="item-price-row">
                <span class="price-val">₩{{ formatPrice(item.price) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="page-footer">
          <button @click="clearWishlist" class="btn-clear-all">
             <i class="fas fa-trash-alt"></i> 위시리스트 전체 비우기
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'WishlistView',
  data() {
    return {
      // 로컬 스토리지에서 데이터 로드
      cartItems: JSON.parse(localStorage.getItem('wishlist') || '[]'),
      selectedItems: [],
      sortOption: 'recent'
    };
  },
  computed: {
    // 전체 선택 로직
    selectAll: {
      get() {
        return this.cartItems.length > 0 && this.selectedItems.length === this.cartItems.length;
      },
      set(value) {
        this.selectedItems = value ? this.cartItems.map(item => item.id) : [];
      }
    }
  },
  methods: {
    getItemImage(item) {
      return item.image || item.imageUrl || 'https://via.placeholder.com/200';
    },
    formatPrice(price) {
      return price ? price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '0';
    },
    isSelected(itemId) {
      return this.selectedItems.includes(itemId);
    },
    // 정렬 기능
    sortItems() {
      if (this.sortOption === 'price_asc') {
        this.cartItems.sort((a, b) => a.price - b.price);
      } else if (this.sortOption === 'price_desc') {
        this.cartItems.sort((a, b) => b.price - a.price);
      } else {
        // 기본 최신순 (id 내림차순 등)
        this.cartItems.sort((a, b) => b.id - a.id);
      }
    },
    // 선택 삭제
    removeSelected() {
      this.cartItems = this.cartItems.filter(item => !this.selectedItems.includes(item.id));
      this.selectedItems = [];
      this.saveWishlist();
    },
    // 전체 비우기
    clearWishlist() {
      if (confirm('위시리스트의 모든 상품을 삭제하시겠습니까?')) {
        this.cartItems = [];
        this.selectedItems = [];
        this.saveWishlist();
      }
    },
    // 스토리지 저장 및 동기화 이벤트 발생
    saveWishlist() {
      localStorage.setItem('wishlist', JSON.stringify(this.cartItems));
      window.dispatchEvent(new Event('wishlist-updated'));
    }
  },
  mounted() {
    // 페이지 진입 시 정렬 상태 적용
    this.sortItems();
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap');

.wishlist-page {
  min-height: 100vh;
  background-color: #ffffff;
  color: #1a1a1a;
  font-family: 'Pretendard', system-ui, -apple-system, sans-serif;
}

.main-container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 48px 24px;
}

/* ----- Hero Section: HomeView 배경색 (#2f3a45) ----- */
.wishlist-hero {
  background-color: #2f3a45;
  padding: 80px 0;
  color: #ffffff;
}

.hero-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 48px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hero-title {
  font-family: 'Montserrat', sans-serif;
  font-size: 40px;
  font-weight: 700;
  line-height: 1.2;
  margin: 0;
}

.accent-count {
  color: #1976d2;
  font-size: 24px;
  vertical-align: top;
  margin-left: 5px;
}

.hero-desc {
  font-size: 15px;
  line-height: 1.6;
  color: #d9d9d9;
  margin-top: 16px;
}

/* ✅ Select 스타일: 옵션 배경색 명시적 지정 */
.modern-select {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  outline: none;
}

.modern-select option {
  background-color: #2f3a45; /* 드롭다운 목록 배경색 수정 */
  color: #fff;
}

/* ----- Premium Checkbox ----- */
.modern-checkbox-container, .card-check-overlay {
  display: flex;
  align-items: center;
  position: relative;
  cursor: pointer;
}

.modern-checkbox-container input, .card-check-overlay input {
  position: absolute;
  opacity: 0;
  width: 0; height: 0;
}

.checkmark {
  height: 20px;
  width: 20px;
  background-color: #eee;
  border-radius: 4px;
  margin-right: 12px;
  position: relative;
  transition: 0.2s;
}

.modern-checkbox-container input:checked ~ .checkmark,
.card-check-overlay input:checked ~ .checkmark {
  background-color: #1976d2;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 7px; top: 3px;
  width: 5px; height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.modern-checkbox-container input:checked ~ .checkmark:after,
.card-check-overlay input:checked ~ .checkmark:after {
  display: block;
}

/* ----- Control Bar ----- */
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.btn-action-delete {
  background: #ff4d4f;
  color: #fff;
  border: none;
  padding: 8px 16px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
}

/* ----- Wishlist Card ----- */
.wishlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

.wishlist-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 20px;
  position: relative;
  transition: all 0.3s ease;
}

.wishlist-card:hover {
  transform: translateY(-4px);
  border-color: #1976d2;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.card-check-overlay {
  position: absolute;
  top: 15px; left: 15px;
  z-index: 10;
}

.card-image-box {
  width: 100%;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.card-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.item-name {
  font-size: 16px;
  font-weight: 700;
  color: #2f3a45;
  margin-bottom: 12px;
  line-height: 1.4;
  height: 44px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 16px;
  min-height: 50px;
}

.spec-tag {
  font-size: 11px;
  background: #f1f3f5;
  color: #495057;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.price-val {
  font-size: 18px;
  font-weight: 800;
  color: #1976d2;
}

/* ----- Footer ----- */
.page-footer {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid #eee;
  text-align: center;
}

.btn-clear-all {
  background: none;
  border: none;
  color: #adb5bd;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
}

.btn-clear-all:hover {
  color: #ff4d4f;
}

@media (max-width: 768px) {
  .hero-inner { flex-direction: column; text-align: center; padding: 40px 20px; }
  .wishlist-grid { grid-template-columns: 1fr 1fr; gap: 12px; }
  .hero-title { font-size: 28px; }
}
</style>