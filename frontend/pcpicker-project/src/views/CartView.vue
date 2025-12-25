<template>
  <div class="wishlist-page">
    <header class="wishlist-hero">
      <div class="circuit-container">
        <svg width="100%" height="100%" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path class="circuit-line line-1" d="M0 200H200L300 300H500L600 200H1000" />
          <path class="circuit-line line-2" d="M1000 800H800L700 700H400L300 800H0" />
          <path class="circuit-line line-3" d="M200 0V300L100 400V600L200 700V1000" />
          <path class="circuit-line line-4" d="M800 1000V700L900 600V400L800 300V0" />
          <circle class="circuit-node" cx="300" cy="300" r="4" />
          <circle class="circuit-node" cx="700" cy="700" r="4" />
        </svg>
      </div>
      <div class="bg-overlay"></div>
      <div class="bg-glow blob-main"></div>

      <div class="hero-inner">
        <div class="hero-text animate-fade-up">
          <div class="hero-badge">
            <span class="dot"></span> My Collection
          </div>
          <h1 class="hero-title">
            Your <span class="highlight-blue">Wishlist</span>
          </h1>
          <p class="hero-desc">
            정교하게 선별된 당신만의 부품 리스트를 관리하세요.<br />
            최적의 구성을 위한 마지막 단계입니다.
          </p>
        </div>

        <div class="hero-actions animate-fade-left">
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
      <div v-if="cartItems.length === 0" class="empty-wishlist animate-fade-up">
        <h2>위시리스트가 비어있습니다</h2>
        <p>나만의 PC를 위해 제품을 추가해보세요.</p>
      </div>

      <div v-else class="wishlist-content">
        <div class="control-bar">
          <div class="control-left">
            <div class="select-all-checkbox" @click="toggleSelectAll">
              <span class="checkmark" :class="{ 'checked': selectAll }"></span>
              <span class="label-txt">전체 선택 ({{ selectedItems.length }}/{{ cartItems.length }})</span>
            </div>
            <button v-show="selectedItems.length > 0" @click.stop="removeSelected" class="btn-action-delete">
              선택 삭제
            </button>
          </div>
        </div>

        <div class="wishlist-grid">
          <div 
            v-for="item in cartItems" 
            :key="item.id" 
            class="wishlist-card"
            :class="{ 'is-selected': isSelected(item.id) }"
            @click="toggleSelect(item.id)" 
          >
            <div class="card-check-indicator">
              <span class="checkmark" :class="{ 'checked': isSelected(item.id) }"></span>
            </div>
            
            <div class="card-image-box">
              <img :src="getItemImage(item)" :alt="item.title || '제품 이미지'" class="card-image">
            </div>

            <div class="card-body">
              <h3 class="item-name">{{ item.title || '제품명 없음' }}</h3>
              
              <div v-if="item.specs && item.specs.length > 0" class="item-specs">
                <span v-for="(spec, specIndex) in item.specs" :key="specIndex" class="spec-tag">
                  {{ spec }}
                </span>
              </div>
              
              <div class="item-price-row">
                <div class="price-info">
                  <span class="price-label">판매가</span>
                  <span class="price-val">₩{{ formatPrice(item.price) }}</span>
                </div>
                <a 
                  v-if="item.shoppingUrl"
                  :href="item.shoppingUrl" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="shop-link"
                  @click.stop
                >
                  <i class="fas fa-shopping-cart"></i> 쇼핑몰 바로가기
                </a>
              </div>
            </div>
          </div>
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
      return item.imageUrl || item.image || 'https://via.placeholder.com/300x200?text=No+Image';
    },
    formatPrice(price) {
      return price ? price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '0';
    },
    isSelected(itemId) {
      return this.selectedItems.includes(itemId);
    },
    toggleSelect(itemId) {
      const index = this.selectedItems.indexOf(itemId);
      if (index > -1) {
        this.selectedItems.splice(index, 1);
      } else {
        this.selectedItems.push(itemId);
      }
    },
    toggleSelectAll() {
      this.selectAll = !this.selectAll;
    },
    sortItems() {
      if (this.sortOption === 'price_asc') {
        this.cartItems.sort((a, b) => a.price - b.price);
      } else if (this.sortOption === 'price_desc') {
        this.cartItems.sort((a, b) => b.price - a.price);
      } else {
        this.cartItems.sort((a, b) => (b.id || 0) - (a.id || 0));
      }
    },
    goToShopLink(link) {
      if (link) window.open(link, '_blank', 'noopener,noreferrer');
    },
    removeSelected() {
      if (confirm(`선택한 ${this.selectedItems.length}개의 상품을 삭제하시겠습니까?`)) {
        this.cartItems = this.cartItems.filter(item => !this.selectedItems.includes(item.id));
        this.selectedItems = [];
        this.saveWishlist();
      }
    },
    clearWishlist() {
      if (confirm('위시리스트의 모든 상품을 삭제하시겠습니까?')) {
        this.cartItems = [];
        this.selectedItems = [];
        this.saveWishlist();
      }
    },
    saveWishlist() {
      localStorage.setItem('wishlist', JSON.stringify(this.cartItems));
      window.dispatchEvent(new Event('wishlist-updated'));
    }
  },
  mounted() {
    this.sortItems();
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

/* ----- 기본 레이아웃 ----- */
.wishlist-page {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Inter', 'Pretendard', sans-serif;
}

/* ----- 히어로 섹션 ----- */
.wishlist-hero {
  position: relative;
  width: 100%;
  padding: 100px 0 80px;
  background: radial-gradient(circle at 50% 50%, #25334a 0%, #1e293b 45%, #1a2436 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  color: #ffffff;
}

.circuit-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.3; }
.circuit-line { stroke: #60a5fa; stroke-width: 1.2; }
.bg-glow { position: absolute; width: 800px; height: 800px; border-radius: 50%; filter: blur(120px); opacity: 0.15; background: #3B82F6; top: 50%; left: 50%; transform: translate(-50%, -50%); }

.hero-inner {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 1100px;
  padding: 0 40px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.hero-title { font-size: 48px; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.highlight-blue { color: #3B82F6; }
.hero-desc { font-size: 17px; color: #94a3b8; margin-top: 15px; line-height: 1.6; }

/* ----- 정렬 셀렉트 (화살표 포함) ----- */
.modern-select-wrapper {
  position: relative;
  display: inline-block;
}

.modern-select-wrapper::after {
  content: '▼';
  font-size: 10px;
  color: #60a5fa;
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  transition: transform 0.3s ease;
}

.modern-select-wrapper:focus-within::after {
  transform: translateY(-50%) rotate(180deg);
}

.modern-select {
  background: #25334a;
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 12px 40px 12px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  width: 170px;
  outline: none;
}

/* ----- 메인 컨텐츠 ----- */
.main-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px;
}

.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.control-left { display: flex; align-items: center; gap: 20px; }

/* ----- 체크박스 공통 ----- */
.checkmark {
  display: inline-block;
  width: 22px; height: 22px;
  background: #e2e8f0;
  border-radius: 6px;
  position: relative;
  transition: 0.2s;
}

.select-all-checkbox input:checked ~ .checkmark,
.checkmark.checked { background: #3B82F6; }

.checkmark:after {
  content: ''; position: absolute; display: none;
  left: 8px; top: 4px; width: 5px; height: 10px;
  border: solid white; border-width: 0 2px 2px 0; transform: rotate(45deg);
}

.select-all-checkbox input:checked ~ .checkmark:after,
.checkmark.checked:after { display: block; }

/* ----- 위시리스트 카드 ----- */
.wishlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
}

.wishlist-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  cursor: pointer;
}

.wishlist-card:hover {
  transform: translateY(-8px);
  border-color: #3B82F6;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08);
}

.wishlist-card.is-selected {
  border-color: #3B82F6;
  background-color: #f8faff;
}

.card-check-indicator { position: absolute; top: 20px; left: 20px; z-index: 5; }

.card-image-box {
  width: 100%;
  height: 180px;
  background: #f8fafc;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.card-image { max-width: 80%; max-height: 80%; object-fit: contain; }

/* 상품명 가독성 */
.item-name {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
  line-height: 1.4;
  height: 56px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 20px;
  min-height: 50px;
}

.spec-tag {
  background: #f1f5f9;
  color: #64748b;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

/* 하단 가격 및 버튼 (정렬 핵심) */
.item-price-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-top: 18px;
  border-top: 1px solid #f1f5f9;
  margin-top: auto;
}

.price-info { display: flex; flex-direction: column; gap: 2px; }
.price-label { font-size: 12px; color: #94a3b8; font-weight: 600; }
.price-val { font-size: 22px; font-weight: 800; color: #1e293b; }

.button-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.shop-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: #3B82F6;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
  border: 1px solid #3B82F6;
}

.shop-link:hover {
  background: #2563eb;
  border-color: #2563eb;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.shop-link i {
  font-size: 14px;
}

/* ----- 기타 버튼 및 애니메이션 ----- */
.btn-action-delete {
  background: #fee2e2;
  color: #ef4444;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.page-footer { margin-top: 60px; text-align: center; }
.btn-clear-all { background: none; border: none; color: #94a3b8; cursor: pointer; text-decoration: underline; font-size: 14px; }

.animate-fade-up { opacity: 0; transform: translateY(20px); animation: fadeUp 0.8s ease forwards; }
@keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .hero-inner { flex-direction: column; align-items: center; text-align: center; gap: 30px; }
  .hero-title { font-size: 36px; }
  .wishlist-grid { grid-template-columns: 1fr; }
}
</style>