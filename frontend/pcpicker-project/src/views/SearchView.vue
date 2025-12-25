<template>
  <div class="search-view">
    <!-- 검색 헤더 -->
    <div class="search-header">
      <h1>PC 제품 검색</h1>
      <p>원하는 PC 제품을 찾아보세요</p>

      <div class="search-bar">
        <div class="search-input-container">
          <i class="fas fa-search search-icon"></i>
          <input
            v-model="searchQuery"
            @keyup.enter="performSearch"
            placeholder="제품명, 브랜드, CPU 등으로 검색"
            class="search-input"
          />
          <button 
            @click="performSearch" 
            class="search-button"
            :disabled="isLoading"
          >
            <i class="fas fa-search"></i> 검색
          </button>
        </div>
      </div>

      <div class="search-meta">
        <span v-if="!isLoading">
          총 <strong>{{ totalItems }}</strong>개의 상품이 있습니다.
        </span>
        <div class="sort-options">
          <label>정렬: </label>
          <select v-model="sortBy" @change="applySorting">
            <option value="price_asc">가격 낮은 순</option>
            <option value="price_desc">가격 높은 순</option>
            <option value="latest">최신순</option>
            <option value="popular">인기순</option>
          </select>
        </div>
      </div>
    </div>

    <div class="search-layout">
      <!-- 필터 사이드바 -->
      <aside class="filter-sidebar">
        <div class="filter-header">
          <h3>필터</h3>
          <button class="clear-filters" @click="resetFilters">
            <i class="fas fa-times"></i> 초기화
          </button>
        </div>

        <div class="filter-section">
          <div class="filter-title" @click="toggleFilter('brand')">
            <h4>브랜드</h4>
            <i class="fas" :class="{'fa-chevron-down': !expandedFilters.brand, 'fa-chevron-up': expandedFilters.brand}"></i>
          </div>
          <div class="filter-options" v-show="expandedFilters.brand">
            <div v-for="b in brandOptions" :key="b" class="filter-option">
              <input 
                type="checkbox" 
                :id="'brand-' + b"
                v-model="filters.brand" 
                :value="b"
                class="filter-checkbox"
              />
              <label :for="'brand-' + b">
                <span class="checkmark"></span>
                {{ b }}
                <span class="filter-count">({{ getFilterCount('brand', b) }})</span>
              </label>
            </div>
          </div>
        </div>

        <div class="filter-section">
          <div class="filter-title" @click="toggleFilter('ram')">
            <h4>RAM</h4>
            <i class="fas" :class="{'fa-chevron-down': !expandedFilters.ram, 'fa-chevron-up': expandedFilters.ram}"></i>
          </div>
          <div class="filter-options" v-show="expandedFilters.ram">
            <div v-for="r in ramOptions" :key="r" class="filter-option">
              <input 
                type="checkbox" 
                :id="'ram-' + r"
                v-model="filters.ram" 
                :value="r"
                class="filter-checkbox"
              />
              <label :for="'ram-' + r">
                <span class="checkmark"></span>
                {{ r }}GB
                <span class="filter-count">({{ getFilterCount('ram', r) }})</span>
              </label>
            </div>
          </div>
        </div>

        <div class="filter-section">
          <div class="filter-title" @click="toggleFilter('ssd')">
            <h4>SSD</h4>
            <i class="fas" :class="{'fa-chevron-down': !expandedFilters.ssd, 'fa-chevron-up': expandedFilters.ssd}"></i>
          </div>
          <div class="filter-options" v-show="expandedFilters.ssd">
            <div v-for="s in ssdOptions" :key="s" class="filter-option">
              <input 
                type="checkbox" 
                :id="'ssd-' + s"
                v-model="filters.ssd" 
                :value="s"
                class="filter-checkbox"
              />
              <label :for="'ssd-' + s">
                <span class="checkmark"></span>
                {{ s }}GB
                <span class="filter-count">({{ getFilterCount('ssd', s) }})</span>
              </label>
            </div>
          </div>
        </div>
      </aside>

      <!-- 상품 목록 -->
      <section class="search-content">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>상품을 불러오는 중입니다...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <i class="fas fa-exclamation-triangle"></i>
          <p>상품을 불러오는 중 오류가 발생했습니다.</p>
          <button @click="fetchProducts" class="retry-button">
            <i class="fas fa-sync-alt"></i> 다시 시도
          </button>
        </div>

        <template v-else>
          <div v-if="filteredProducts.length === 0" class="empty-state">
            <i class="fas fa-search"></i>
            <h3>검색 결과가 없습니다</h3>
            <p>검색어를 변경하거나 필터를 조정해 보세요.</p>
            <button @click="resetFilters" class="reset-button">
              필터 초기화
            </button>
          </div>

          <template v-else>
            <div class="product-grid">
              <ProductCard
                v-for="product in paginatedProducts"
                :key="product.id"
                :product="product"
                @add-to-cart="addToCart"
              />
            </div>

            <!-- 페이지네이션 -->
            <div v-if="totalPages > 1" class="pagination">
              <button 
                class="pagination-button"
                :disabled="currentPage === 1"
                @click="changePage(currentPage - 1)"
              >
                <i class="fas fa-chevron-left"></i> 이전
              </button>

              <div class="page-numbers">
                <button 
                  v-for="page in visiblePages" 
                  :key="page"
                  :class="['page-number', { active: currentPage === page }]"
                  @click="changePage(page)"
                >
                  {{ page }}
                </button>
              </div>

              <button 
                class="pagination-button"
                :disabled="currentPage === totalPages"
                @click="changePage(currentPage + 1)"
              >
                다음 <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </template>
        </template>
      </section>
    </div>
  </div>
</template>

<script>
import apiClient from '@/services/api'
import ProductCard from '@/components/ProductCard.vue'

export default {
  name: 'SearchView',
  components: {
    ProductCard
  },
  data() {
    return {
      searchQuery: '',
      isLoading: false,
      error: null,

      searchResults: [],
      filteredProducts: [],

      currentPage: 1,
      itemsPerPage: 12,
      maxVisiblePages: 5,
      sortBy: 'latest',

      filters: {
        brand: [],
        ram: [],
        ssd: []
      },

      expandedFilters: {
        brand: true,
        ram: true,
        ssd: true
      },

      brandOptions: ['Apple', 'Samsung', 'LG', 'ASUS', 'MSI', 'Dell', 'HP'],
      ramOptions: [4, 8, 16, 32, 64],
      ssdOptions: [128, 256, 512, 1024, 2048],
      
      // For filter counts
      filterCounts: {
        brand: {},
        ram: {},
        ssd: {}
      }
    }
  },
  computed: {
    totalItems() {
      return this.filteredProducts.length;
    },
    totalPages() {
      return Math.ceil(this.filteredProducts.length / this.itemsPerPage);
    },
    paginatedProducts() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.filteredProducts.slice(start, start + this.itemsPerPage);
    },
    visiblePages() {
      const range = [];
      const half = Math.floor(this.maxVisiblePages / 2);
      let start = Math.max(1, this.currentPage - half);
      let end = Math.min(this.totalPages, start + this.maxVisiblePages - 1);
      
      if (end - start + 1 < this.maxVisiblePages) {
        start = Math.max(1, end - this.maxVisiblePages + 1);
      }
      
      for (let i = start; i <= end; i++) {
        range.push(i);
      }
      
      return range;
    }
  },
  watch: {
    filters: {
      deep: true,
      handler() {
        this.currentPage = 1;
        this.applyFilters();
      }
    },
    searchQuery() {
      this.currentPage = 1;
      this.performSearch();
    },
    $route() {
      this.checkRouteQuery();
    }
  },
  methods: {
    async fetchProducts() {
      this.isLoading = true;
      this.error = null;
      
      try {
        const { data } = await apiClient.get('/products/products/');
        
        this.searchResults = data.map(p => ({
          id: p.id,
          name: p.name,
          title: p.name, // For backward compatibility
          brand: p.brand || '기타',
          price: p.price || 0,
          cpu: p.cpu || '정보 없음',
          ram: p.ram || 0,
          ssd: p.ssd || 0,
          image: p.image || p.image_url || '',
          stock: p.stock || 0,
          rating: p.rating || 0,
          reviewCount: p.review_count || 0,
          isNew: p.is_new || false,
          discount: p.discount || 0,
          originalPrice: p.original_price || p.price || 0
        }));
        
        this.filteredProducts = [...this.searchResults];
        this.calculateFilterCounts();
      } catch (error) {
        console.warn('API에서 상품을 불러오지 못했습니다. 샘플 데이터를 표시합니다.');
        
        // Sample data
        this.searchResults = [
          {
            id: 1,
            name: '삼성 갤럭시북3 프로',
            title: '삼성 갤럭시북3 프로',
            brand: 'Samsung',
            price: 1990000,
            cpu: 'Intel Core i7-1360P',
            ram: 16,
            ssd: 512,
            image: 'https://images.samsung.com/kdp/goods/2023/02/01/6b3c0f1c-0c2a-4d9b-8d1a-5b5d5c5b5b5b',
            stock: 10,
            rating: 4.5,
            reviewCount: 24,
            isNew: true,
            discount: 10,
            originalPrice: 2190000,
            createdAt: '2023-02-15T00:00:00Z'
          },
          {
            id: 2,
            name: 'LG 그램 16',
            title: 'LG 그램 16',
            brand: 'LG',
            price: 1890000,
            cpu: 'Intel Core i5-1240P',
            ram: 16,
            ssd: 512,
            image: 'https://www.lge.co.kr/kr/images/gram/gallery/select/16zt90q-ko_01_v1.jpg',
            stock: 15,
            rating: 4.7,
            reviewCount: 32,
            isNew: false,
            discount: 5,
            originalPrice: 1990000,
            createdAt: '2023-01-20T00:00:00Z'
          },
          {
            id: 3,
            name: '맥북 프로 14',
            title: '맥북 프로 14',
            brand: 'Apple',
            price: 2690000,
            cpu: 'Apple M2 Pro',
            ram: 16,
            ssd: 1024,
            image: 'https://www.apple.com/v/macbook-pro-14-and-16/b/images/overview/hero/hero_intro_endframe__e6khcva4hkeq_large.jpg',
            stock: 8,
            rating: 4.9,
            reviewCount: 45,
            isNew: true,
            discount: 0,
            originalPrice: 2690000,
            createdAt: '2023-03-01T00:00:00Z'
          },
          {
            id: 4,
            name: 'LG 울트라PC 15',
            title: 'LG 울트라PC 15',
            brand: 'LG',
            price: 1290000,
            cpu: 'Intel Core i5-1235U',
            ram: 8,
            ssd: 256,
            image: 'https://www.lge.co.kr/kr/images/ultrapc/gallery/select/15u70q-ko_01_v1.jpg',
            stock: 5,
            rating: 4.2,
            reviewCount: 12,
            isNew: false,
            discount: 8,
            originalPrice: 1390000,
            createdAt: '2022-11-10T00:00:00Z'
          },
          {
            id: 5,
            name: '삼성 갤럭시북2 프로 360',
            title: '삼성 갤럭시북2 프로 360',
            brand: 'Samsung',
            price: 1790000,
            cpu: 'Intel Core i7-1260P',
            ram: 16,
            ssd: 512,
            image: 'https://images.samsung.com/kdp/goods/2022/01/04/6b3c0f1c-0c2a-4d9b-8d1a-5b5d5c5b5b5b',
            stock: 3,
            rating: 4.6,
            reviewCount: 28,
            isNew: false,
            discount: 15,
            originalPrice: 2090000,
            createdAt: '2022-12-05T00:00:00Z'
          }
        ];
        
        this.filteredProducts = [...this.searchResults];
        this.calculateFilterCounts();
      } finally {
        this.isLoading = false;
      }
    },
    
    calculateFilterCounts() {
      // Reset counts
      this.filterCounts = {
        brand: {},
        ram: {},
        ssd: {}
      };
      
      // Calculate counts for each filter option
      this.searchResults.forEach(product => {
        // Count brands
        if (product.brand) {
          this.filterCounts.brand[product.brand] = (this.filterCounts.brand[product.brand] || 0) + 1;
        }
        
        // Count RAM
        if (product.ram) {
          this.filterCounts.ram[product.ram] = (this.filterCounts.ram[product.ram] || 0) + 1;
        }
        
        // Count SSD
        if (product.ssd) {
          this.filterCounts.ssd[product.ssd] = (this.filterCounts.ssd[product.ssd] || 0) + 1;
        }
      });
    },
    
    getFilterCount(filterType, value) {
      return this.filterCounts[filterType]?.[value] || 0;
    },
    
    toggleFilter(filterType) {
      this.expandedFilters[filterType] = !this.expandedFilters[filterType];
    },
    
    performSearch() {
      if (!this.searchQuery.trim()) {
        this.filteredProducts = [...this.searchResults];
        return;
      }
      
      const q = this.searchQuery.toLowerCase().trim();
      this.filteredProducts = this.searchResults.filter(p =>
        (p.name && p.name.toLowerCase().includes(q)) ||
        (p.title && p.title.toLowerCase().includes(q)) ||
        (p.brand && p.brand.toLowerCase().includes(q)) ||
        (p.cpu && p.cpu.toLowerCase().includes(q))
      );
    },

    applyFilters() {
      let result = [...this.searchResults];
      
      // Apply search query filter
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase().trim();
        result = result.filter(p => 
          (p.name && p.name.toLowerCase().includes(q)) ||
          (p.title && p.title.toLowerCase().includes(q)) ||
          (p.brand && p.brand.toLowerCase().includes(q)) ||
          (p.cpu && p.cpu.toLowerCase().includes(q))
        );
      }

      // Apply brand filter
      if (this.filters.brand.length) {
        result = result.filter(p => 
          p.brand && this.filters.brand.includes(p.brand)
        );
      }

      // Apply RAM filter
      if (this.filters.ram.length) {
        result = result.filter(p => 
          p.ram !== undefined && this.filters.ram.includes(p.ram)
        );
      }

      // Apply SSD filter
      if (this.filters.ssd.length) {
        result = result.filter(p => 
          p.ssd !== undefined && this.filters.ssd.includes(p.ssd)
        );
      }
      
      // Apply sorting
      result = this.sortProducts(result);
      
      this.filteredProducts = result;
    },
    
    resetFilters() {
      this.filters = {
        brand: [],
        ram: [],
        ssd: []
      };
      this.searchQuery = '';
      this.currentPage = 1;
      this.sortBy = 'latest';
      this.filteredProducts = [...this.searchResults];
      this.applySorting();
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        // Scroll to top of product grid
        const element = document.querySelector('.search-content');
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }
    },
    
    applySorting() {
      this.filteredProducts = this.sortProducts([...this.filteredProducts]);
      this.currentPage = 1;
    },
    
    sortProducts(products) {
      const sorted = [...products];
      
      switch (this.sortBy) {
        case 'price_asc':
          return sorted.sort((a, b) => (a.price || 0) - (b.price || 0));
        case 'price_desc':
          return sorted.sort((a, b) => (b.price || 0) - (a.price || 0));
        case 'latest':
          // Assuming there's a 'createdAt' field, adjust as needed
          return sorted.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
        case 'popular':
          // Assuming there's a 'rating' or 'reviewCount' field
          return sorted.sort((a, b) => {
            const aScore = (a.rating || 0) * (a.reviewCount || 1);
            const bScore = (b.rating || 0) * (b.reviewCount || 1);
            return bScore - aScore;
          });
        default:
          return sorted;
      }
    },
    
    addToCart(product) {
      // Emit event to parent or handle cart addition
      this.$emit('add-to-cart', product);
      // Optional: Show notification or toast
      this.$toast.success(`${product.name}이(가) 장바구니에 추가되었습니다.`);
    },
    
    checkRouteQuery() {
      // Handle route query parameters if needed
      const query = this.$route.query;
      if (query.search) {
        this.searchQuery = query.search;
      }
      // Add more query parameter handling as needed
    }
  },
  created() {
    this.checkRouteQuery();
    this.fetchProducts();
  },
  
  mounted() {
    // Initialize any third-party libraries or event listeners here
  },
  
  beforeUnmount() {
    // Clean up any event listeners or timers
  }
}
</script>

<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>

<style scoped>
.search-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  min-height: calc(100vh - 200px);
}

.search-header {
  text-align: center;
  margin-bottom: 3rem;
  padding: 0 1rem;
}

.search-header h1 {
  font-size: 2.25rem;
  color: #1f2937;
  margin-bottom: 0.75rem;
  font-weight: 700;
}

.search-header p {
  font-size: 1.1rem;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.search-bar {
  max-width: 700px;
  margin: 0 auto 2rem;
  position: relative;
}

.search-input-container {
  display: flex;
  border: 2px solid #e5e7eb;
  border-radius: 50px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.search-input-container:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.search-icon {
  padding: 0 1.25rem;
  color: #9ca3af;
  display: flex;
  align-items: center;
  font-size: 1.1rem;
}

.search-input {
  flex: 1;
  padding: 0.9rem 0.5rem 0.9rem 0;
  border: none;
  outline: none;
  font-size: 1rem;
  color: #1f2937;
  background: transparent;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-button {
  padding: 0 1.75rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.search-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.search-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-1px);
}

.search-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 700px;
  margin: 0 auto;
  font-size: 0.95rem;
  color: #6b7280;
}

.search-meta strong {
  color: #3b82f6;
  font-weight: 600;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-options select {
  padding: 0.4rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: white;
  color: #4b5563;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.sort-options select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

/* Search Layout */
.search-layout {
  display: flex;
  gap: 2rem;
  position: relative;
}

/* Filter Sidebar */
.filter-sidebar {
  width: 280px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  height: fit-content;
  position: sticky;
  top: 2rem;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.filter-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.clear-filters {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.clear-filters:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.filter-section {
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 1.25rem;
}

.filter-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.filter-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 0.25rem 0;
}

.filter-title h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.filter-title i {
  color: #9ca3af;
  font-size: 0.8rem;
  transition: transform 0.2s;
}

.filter-options {
  margin-top: 0.75rem;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.filter-option {
  margin-bottom: 0.5rem;
}

.filter-checkbox {
  position: absolute;
  opacity: 0;
  height: 0;
  width: 0;
}

.filter-option label {
  display: flex;
  align-items: center;
  padding: 0.4rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  font-size: 0.95rem;
  color: #4b5563;
}

.filter-option label:hover {
  background: #f9fafb;
}

.checkmark {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  margin-right: 0.75rem;
  position: relative;
  transition: all 0.2s;
}

.filter-checkbox:checked + label .checkmark {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.filter-checkbox:checked + label .checkmark:after {
  content: '';
  position: absolute;
  left: 5px;
  top: 1px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.filter-count {
  margin-left: auto;
  color: #9ca3af;
  font-size: 0.85rem;
}

/* Search Content */
.search-content {
  flex: 1;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem;
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #6b7280;
  font-size: 1.1rem;
  margin-top: 1rem;
}

/* Error State */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem;
  text-align: center;
  color: #ef4444;
}

.error-state i {
  font-size: 3rem;
  margin-bottom: 1.5rem;
  opacity: 0.8;
}

.error-state p {
  color: #6b7280;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.retry-button {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.6rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.retry-button:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem;
  text-align: center;
}

.empty-state i {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.empty-state h3 {
  color: #1f2937;
  font-size: 1.5rem;
  margin-bottom: 0.75rem;
}

.empty-state p {
  color: #6b7280;
  font-size: 1.05rem;
  margin-bottom: 1.5rem;
  max-width: 400px;
}

.reset-button {
  background: #f3f4f6;
  color: #4b5563;
  border: none;
  border-radius: 6px;
  padding: 0.6rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-button:hover {
  background: #e5e7eb;
}

/* Product Grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 3rem;
}

.pagination-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  color: #4b5563;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-button:not(:disabled):hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #1f2937;
}

.pagination-button i {
  font-size: 0.8rem;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.page-number {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  color: #4b5563;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.page-number:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.page-number.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
  font-weight: 500;
}

/* Responsive Styles */
@media (max-width: 1024px) {
  .search-layout {
    flex-direction: column;
  }
  
  .filter-sidebar {
    width: 100%;
    position: static;
    margin-bottom: 2rem;
  }
  
  .product-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 640px) {
  .search-header h1 {
    font-size: 1.75rem;
  }
  
  .search-meta {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .product-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .page-numbers {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .search-view {
    padding: 1.5rem 1rem;
  }
  
  .product-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .pagination-button, 
  .page-number {
    width: 36px;
    height: 36px;
    font-size: 0.85rem;
  }
}
</style>