<template>
  <div class="wishlist-page">
    <section class="wishlist-hero">
      <div class="hero-inner">
        <div class="hero-text">
          <h1 class="hero-title">
            Your Wishlist<br />
            <span class="item-count">찜한 상품 ({{ cartItems.length }})</span>
          </h1>
          <p class="hero-desc">
            관심 있는 제품을 한눈에 비교하고 관리하세요.<br />
            나만의 구성을 완성하기 위한 최적의 아이템들입니다.
          </p>
        </div>

        <div class="hero-actions">
          <div class="sort-options">
            <select v-model="sortOption" @change="sortItems">
              <option value="recent">최신순</option>
              <option value="price_asc">낮은 가격순</option>
              <option value="price_desc">높은 가격순</option>
            </select>
          </div>
        </div>
      </div>
    </section>

    <div class="container">
      <div v-if="cartItems.length === 0" class="empty-wishlist">
        <div class="empty-icon">
          <i class="fas fa-heart"></i>
        </div>
        <h2>찜한 상품이 없습니다</h2>
        <p>관심 있는 PC 부품을 찾아 찜 목록에 추가해 보세요.</p>
        <router-link to="/community" class="browse-btn">제품 둘러보기</router-link>
      </div>

      <div v-else class="wishlist-content">
        <div class="control-bar">
          <label class="select-all">
            <input type="checkbox" v-model="selectAll" @change="toggleSelectAll">
            <span class="custom-checkbox"></span>
            전체 선택 ({{ selectedItems.length }}/{{ cartItems.length }})
          </label>
          <button 
            v-if="selectedItems.length > 0" 
            @click="removeSelected" 
            class="btn-outline-danger"
          >
            선택 삭제
          </button>
        </div>

        <div class="wishlist-grid">
          <div 
            v-for="(item, index) in cartItems" 
            :key="item.id" 
            class="wishlist-card"
            :class="{ 'is-selected': isSelected(item.id) }"
          >
            <div class="card-select">
              <input 
                type="checkbox" 
                :value="item.id"
                v-model="selectedItems"
              >
            </div>
            
            <div class="card-image-wrapper">
              <img :src="getItemImage(item)" :alt="item.name" class="card-image">
            </div>

            <div class="card-body">
              <h3 class="item-name">{{ item.name }}</h3>
              <div class="item-info">
                <span class="price-label">금액</span>
                <span class="item-price">{{ formatPrice(item.price) }}원</span>
              </div>
              
              <div class="card-footer">
                <button @click="removeItem(index)" class="btn-icon-remove" title="삭제">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="page-footer">
          <button @click="clearWishlist" class="btn-text-only">
            <i class="fas fa-eraser"></i> 위시리스트 전체 비우기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Logic은 기존과 동일하되 디자인에 맞게 유지
export default {
  name: 'WishlistView',
  data() {
    return {
      cartItems: JSON.parse(localStorage.getItem('wishlist') || '[]'),
      selectedItems: [],
      sortOption: 'recent'
    };
  },
  computed: {
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
    toggleSelectAll() {
      // computed setter에서 자동 처리됨
    },
    removeItem(index) {
      this.cartItems.splice(index, 1);
      this.saveWishlist();
    },
    removeSelected() {
      this.cartItems = this.cartItems.filter(item => !this.selectedItems.includes(item.id));
      this.selectedItems = [];
      this.saveWishlist();
    },
    clearWishlist() {
      if (confirm('찜 목록을 모두 비우시겠습니까?')) {
        this.cartItems = [];
        this.selectedItems = [];
        this.saveWishlist();
      }
    },
    sortItems() {
      if (this.sortOption === 'price_asc') this.cartItems.sort((a, b) => a.price - b.price);
      else if (this.sortOption === 'price_desc') this.cartItems.sort((a, b) => b.price - a.price);
      else this.cartItems.sort((a, b) => b.id - a.id);
    },
    saveWishlist() {
      localStorage.setItem('wishlist', JSON.stringify(this.cartItems));
      window.dispatchEvent(new Event('wishlist-updated'));
    }
  }
}
</script>

<style scoped>
/* ----- Base Layout ----- */
.wishlist-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  font-family: 'Pretendard', system-ui, -apple-system, sans-serif;
}

.container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 48px 24px;
}

/* ----- Hero Header (HomeView 스타일 적용) ----- */
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
  font-size: 36px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 12px;
}

.item-count {
  font-size: 20px;
  color: #1976d2;
  font-weight: 500;
}

.hero-desc {
  font-size: 15px;
  color: #d9d9d9;
  line-height: 1.6;
}

.sort-options select {
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  outline: none;
  cursor: pointer;
}

.sort-options select option {
  background-color: #2f3a45;
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

.select-all {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #444;
  cursor: pointer;
}

.btn-outline-danger {
  padding: 8px 16px;
  border: 1px solid #ff4d4f;
  background: white;
  color: #ff4d4f;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

.btn-outline-danger:hover {
  background: #ff4d4f;
  color: white;
}

/* ----- Wishlist Grid & Card ----- */
.wishlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

.wishlist-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  position: relative;
  border: 1px solid #eee;
}

.wishlist-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.wishlist-card.is-selected {
  border-color: #1976d2;
  background-color: #f0f7ff;
}

.card-select {
  position: absolute;
  top: 15px;
  left: 15px;
  z-index: 2;
}

.card-image-wrapper {
  width: 100%;
  height: 200px;
  background: #f1f1f1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: 0.3s;
}

.card-body {
  padding: 20px;
}

.item-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  height: 44px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.price-label {
  font-size: 13px;
  color: #888;
}

.item-price {
  font-size: 18px;
  font-weight: 700;
  color: #ff4d4f;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #f5f5f5;
  padding-top: 12px;
}

.btn-icon-remove {
  background: none;
  border: none;
  color: #bbb;
  cursor: pointer;
  font-size: 18px;
  transition: 0.2s;
}

.btn-icon-remove:hover {
  color: #ff4d4f;
}

/* ----- Empty State ----- */
.empty-wishlist {
  text-align: center;
  padding: 100px 0;
}

.empty-icon {
  width: 100px;
  height: 100px;
  background: #fff0f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.empty-icon i {
  font-size: 40px;
  color: #ffb6c1;
}

.empty-wishlist h2 {
  font-size: 24px;
  color: #2f3a45;
  margin-bottom: 12px;
}

.empty-wishlist p {
  color: #888;
  margin-bottom: 32px;
}

.browse-btn {
  display: inline-block;
  padding: 14px 32px;
  background-color: #1976d2;
  color: white;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  transition: 0.3s;
}

.browse-btn:hover {
  background-color: #1565c0;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

/* ----- Footer ----- */
.page-footer {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}

.btn-text-only {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
}

.btn-text-only:hover {
  color: #666;
}

/* ----- Mobile Responsive ----- */
@media (max-width: 768px) {
  .hero-inner {
    flex-direction: column;
    text-align: center;
    gap: 24px;
    padding: 0 24px;
  }
  
  .wishlist-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  
  .card-image-wrapper {
    height: 150px;
  }
}
</style>