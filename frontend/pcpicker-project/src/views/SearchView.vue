<template>
  <div class="search-page">
    <div class="search-container">
      <header class="page-header">
        <div class="header-content">
          <div class="header-text">
            <h1 class="title">상품 <span>검색</span></h1>
            <p class="subtitle">원하는 PC 제품을 검색하고 비교해보세요.</p>
          </div>
        </div>

        <div class="search-wrapper">
          <div class="search-bar">
            <input 
              type="text" 
              v-model="searchQuery" 
              @keyup.enter="performSearch"
              placeholder="제품명, 브랜드, 모델명 등으로 검색해보세요..."
              class="search-input"
            >
            <button @click="performSearch" class="search-button">
              <i class="fas fa-search"></i> 검색
            </button>
          </div>
        </div>
      </header>

      <div class="search-layout">
        <!-- Filter Sidebar -->
        <div class="filter-sidebar">
          <div class="filter-header">
            <h3>검색 필터</h3>
            <button class="reset-filters" @click="resetFilters">초기화</button>
          </div>
          
          <!-- Product Type Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('productType')">
              <span>제품 유형</span>
              <i class="fas" :class="expandedSections.productType ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.productType">
              <label v-for="option in productTypeOptions" :key="option.value">
                <input type="checkbox" v-model="filters.productType" :value="option.value">
                <span class="checkmark"></span>
                <span class="option-label">{{ option.label }}</span>
              </label>
            </div>
          </div>

          <!-- Brand Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('brand')">
              <span>브랜드</span>
              <i class="fas" :class="expandedSections.brand ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.brand">
              <label v-for="option in brandOptions" :key="option.value">
                <input type="checkbox" v-model="filters.brand" :value="option.value">
                <span class="checkmark"></span>
                <span class="option-label">{{ option.label }}</span>
              </label>
            </div>
          </div>

          <!-- OS Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('os')">
              <span>운영체제</span>
              <i class="fas" :class="expandedSections.os ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.os">
              <label v-for="option in osOptions" :key="option.value">
                <input type="checkbox" v-model="filters.os" :value="option.value">
                <span class="checkmark"></span>
                <span class="option-label">{{ option.label }}</span>
              </label>
            </div>
          </div>

          <!-- CPU Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('cpu')">
              <span>프로세서</span>
              <i class="fas" :class="expandedSections.cpu ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.cpu">
              <div class="subtitle">인텔 코어 시리즈</div>
              <div class="checkbox-group">
                <label v-for="option in cpuIntelOptions" :key="'intel-'+option.value">
                  <input type="checkbox" v-model="filters.cpu" :value="'intel-'+option.value">
                  <span class="checkmark"></span>
                  <span class="option-label">i{{ option.label }}</span>
                </label>
              </div>
              <div class="subtitle">AMD 라이젠 시리즈</div>
              <div class="checkbox-group">
                <label v-for="option in cpuAmdOptions" :key="'amd-'+option.value">
                  <input type="checkbox" v-model="filters.cpu" :value="'amd-'+option.value">
                  <span class="checkmark"></span>
                  <span class="option-label">R{{ option.label }}</span>
                </label>
              </div>
              <div class="checkbox-group">
                <label>
                  <input type="checkbox" v-model="filters.cpu" value="others">
                  <span class="checkmark"></span>
                  <span class="option-label">기타</span>
                </label>
              </div>
            </div>
          </div>

          <!-- RAM Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('ram')">
              <span>메모리 (RAM)</span>
              <i class="fas" :class="expandedSections.ram ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.ram">
              <label v-for="option in ramOptions" :key="option.value">
                <input type="checkbox" v-model="filters.ram" :value="option.value">
                <span class="checkmark"></span>
                <span class="option-label">{{ option.label }}</span>
              </label>
            </div>
          </div>

          <!-- SSD Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('ssd')">
              <span>저장장치 (SSD)</span>
              <i class="fas" :class="expandedSections.ssd ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.ssd">
              <label v-for="option in ssdOptions" :key="option.value">
                <input type="checkbox" v-model="filters.ssd" :value="option.value">
                <span class="checkmark"></span>
                <span class="option-label">{{ option.label }}</span>
              </label>
            </div>
          </div>

          <!-- Weight Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('weight')">
              <span>무게</span>
              <i class="fas" :class="expandedSections.weight ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.weight">
              <label v-for="option in weightOptions" :key="option.value">
                <input type="checkbox" v-model="filters.weight" :value="option.value">
                <span class="checkmark"></span>
                <span class="option-label">{{ option.label }}</span>
              </label>
            </div>
          </div>

          <!-- Display Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('display')">
              <span>디스플레이</span>
              <i class="fas" :class="expandedSections.display ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.display">
              <label v-for="option in displayOptions" :key="option.value">
                <input type="checkbox" v-model="filters.display" :value="option.value">
                <span class="checkmark"></span>
                <span class="option-label">{{ option.label }}</span>
              </label>
            </div>
          </div>

          <!-- Power Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('power')">
              <span>파워</span>
              <i class="fas" :class="expandedSections.power ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.power">
              <label v-for="option in powerOptions" :key="option.value">
                <input type="checkbox" v-model="filters.power" :value="option.value">
                <span class="checkmark"></span>
                <span class="option-label">{{ option.label }}</span>
              </label>
            </div>
          </div>

          <!-- Price Section -->
          <div class="filter-section">
            <div class="filter-title" @click="toggleSection('price')">
              <span>가격대</span>
              <i class="fas" :class="expandedSections.price ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="filter-options" v-show="expandedSections.price">
              <label v-for="option in priceOptions" :key="option.value">
                <input type="checkbox" v-model="filters.price" :value="option.value">
                <span class="checkmark"></span>
                <span class="option-label">{{ option.label }}</span>
              </label>
            </div>
          </div>
        </div>
          <h3>Brand</h3>
          <div class="filter-options" v-for="(option, index) in brandOptions" :key="'brand-'+index">
            <label>
              <input type="checkbox" v-model="filters.brand" :value="option.value">
              {{ option.label }}
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>OS</h3>
          <div class="filter-options" v-for="(option, index) in osOptions" :key="'os-'+index">
            <label>
              <input type="checkbox" v-model="filters.os" :value="option.value">
              {{ option.label }}
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>CPU</h3>
          <div class="filter-options" v-for="(option, index) in cpuOptions" :key="'cpu-'+index">
            <label>
              <input type="checkbox" v-model="filters.cpu" :value="option.value">
              {{ option.label }}
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>RAM</h3>
          <div class="filter-options" v-for="(option, index) in ramOptions" :key="'ram-'+index">
            <label>
              <input type="checkbox" v-model="filters.ram" :value="option.value">
              {{ option.label }}
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>SSD</h3>
          <div class="filter-options" v-for="(option, index) in ssdOptions" :key="'ssd-'+index">
            <label>
              <input type="checkbox" v-model="filters.ssd" :value="option.value">
              {{ option.label }}
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>Weight</h3>
          <div class="filter-options" v-for="(option, index) in weightOptions" :key="'weight-'+index">
            <label>
              <input type="checkbox" v-model="filters.weight" :value="option.value">
              {{ option.label }}
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>Display</h3>
          <div class="filter-options" v-for="(option, index) in displayOptions" :key="'display-'+index">
            <label>
              <input type="checkbox" v-model="filters.display" :value="option.value">
              {{ option.label }}
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>Power</h3>
          <div class="filter-options" v-for="(option, index) in powerOptions" :key="'power-'+index">
            <label>
              <input type="checkbox" v-model="filters.power" :value="option.value">
              {{ option.label }}
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>Price</h3>
          <div class="filter-options" v-for="(option, index) in priceOptions" :key="'price-'+index">
            <label>
              <input type="checkbox" v-model="filters.price" :value="option.value">
              {{ option.label }}
            </label>
          </div>
        </div>
        </div> <!-- Close filter-sidebar -->

        <!-- Main Content Area -->
      <div class="search-content">
        <div v-if="isLoading" class="state-container">
          <div class="custom-loader"></div>
          <p>검색 중입니다...</p>
        </div>
        
        <template v-else>
          <div v-if="searchPerformed">
            <div v-if="searchResults && searchResults.length > 0" class="search-results">
              <div class="results-header">
                <h2>"{{ searchQuery }}" 검색 결과</h2>
                <span class="results-count">총 {{ searchResults.length }}개의 상품을 찾았습니다.</span>
              </div>
              
              <div class="product-grid">
                <div v-for="(result, index) in searchResults" :key="index" class="product-card">
                  <div class="product-image" :style="{ backgroundImage: 'url(' + (result.image || 'https://via.placeholder.com/200') + ')' }">
                    <div class="product-badges">
                      <span v-if="result.isNew" class="badge new">NEW</span>
                      <span v-if="result.discount" class="badge discount">-{{ result.discount }}%</span>
                    </div>
                  </div>
                  <div class="product-info">
                    <div class="product-brand">{{ result.brand || '브랜드' }}</div>
                    <h3 class="product-title">{{ result.title }}</h3>
                    <div class="product-specs">
                      <span v-if="result.cpu"><i class="fas fa-microchip"></i> {{ result.cpu }}</span>
                      <span v-if="result.ram"><i class="fas fa-memory"></i> {{ result.ram }}GB</span>
                      <span v-if="result.ssd"><i class="fas fa-hdd"></i> {{ result.ssd }}GB</span>
                    </div>
                    <div class="product-price">
                      <span class="current-price">{{ formatPrice(result.price) }}원</span>
                      <span v-if="result.originalPrice" class="original-price">{{ formatPrice(result.originalPrice) }}원</span>
                    </div>
                    <div class="product-actions">
                      <button class="btn-compare" @click.stop="addToCompare(result)">
                        <i class="fas fa-balance-scale"></i> 비교
                      </button>
                      <button class="btn-cart" @click.stop="addToCart(result)">
                        <i class="fas fa-shopping-cart"></i> 장바구니
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="state-container no-results">
              <div class="empty-icon">🔍</div>
              <h3>"{{ searchQuery }}"에 대한 검색 결과가 없습니다.</h3>
              <p>다른 검색어를 시도하거나 필터를 조정해보세요.</p>
            </div>
          </div>
          
          <div v-else class="state-container search-tips">
            <div class="empty-icon">💡</div>
            <h3>검색 팁</h3>
            <ul>
              <li>검색어의 철자가 정확한지 확인해주세요.</li>
              <li>더 일반적인 검색어로 시도해보세요.</li>
              <li>필터를 사용하여 검색 범위를 좁혀보세요.</li>
            </ul>
          </div>
        </template>
      </div> <!-- Close search-content -->
    </div> <!-- Close search-layout -->

</template>

<script>
export default {
  name: 'SearchView',
  data() {
    return {
      searchQuery: this.$route.query.q || '',
      searchResults: null,
      isLoading: false,
      searchPerformed: false,
      
      // Filter options data
      productTypeOptions: [
        { value: 'laptop', label: '노트북' },
        { value: 'desktop', label: '데스크탑' },
        { value: 'aio', label: '올인원' },
        { value: 'others', label: '기타' }
      ],
      brandOptions: [
        { value: 'apple', label: 'Apple' },
        { value: 'samsung', label: 'Samsung' },
        { value: 'lg', label: 'LG' },
        { value: 'asus', label: 'ASUS' },
        { value: 'msi', label: 'MSI' },
        { value: 'dell', label: 'Dell' },
        { value: 'hp', label: 'HP' },
        { value: 'lenovo', label: 'Lenovo' },
        { value: 'others', label: '기타' }
      ],
      osOptions: [
        { value: 'macos', label: 'macOS' },
        { value: 'windows', label: 'Windows' },
        { value: 'linux', label: 'Linux' },
        { value: 'chromeos', label: 'Chrome OS' },
        { value: 'others', label: '기타' }
      ],
      cpuIntelOptions: [
        { value: '3', label: '3' },
        { value: '5', label: '5' },
        { value: '7', label: '7' },
        { value: '9', label: '9' }
      ],
      cpuAmdOptions: [
        { value: '3', label: '3' },
        { value: '5', label: '5' },
        { value: '7', label: '7' },
        { value: '9', label: '9' }
      ],
      ramOptions: [
        { value: '4', label: '4GB' },
        { value: '8', label: '8GB' },
        { value: '16', label: '16GB' },
        { value: '32', label: '32GB' },
        { value: '64', label: '64GB' },
        { value: 'others', label: '기타' }
      ],
      ssdOptions: [
        { value: '128', label: '128GB' },
        { value: '256', label: '256GB' },
        { value: '512', label: '512GB' },
        { value: '1024', label: '1TB' },
        { value: '2048', label: '2TB' },
        { value: 'others', label: '기타' }
      ],
      weightOptions: [
        { value: '0-1', label: '~1kg' },
        { value: '1-2', label: '1kg~2kg' },
        { value: '2-3', label: '2kg~3kg' },
        { value: '3-', label: '3kg~' },
        { value: 'others', label: '기타' }
      ],
      displayOptions: [
        { value: '13', label: '13인치' },
        { value: '14', label: '14인치' },
        { value: '15', label: '15인치' },
        { value: '16', label: '16인치' },
        { value: '17', label: '17인치' },
        { value: '24', label: '24인치' },
        { value: '27', label: '27인치' },
        { value: '32', label: '32인치' },
        { value: 'others', label: '기타' }
      ],
      powerOptions: [
        { value: '500-600', label: '500W~600W' },
        { value: '650-750', label: '650W~750W' },
        { value: '850-', label: '850W~' },
        { value: 'others', label: '기타' }
      ],
      priceOptions: [
        { value: '0-1000000', label: '~100만원' },
        { value: '1000000-2000000', label: '100만원~200만원' },
        { value: '2000000-', label: '200만원~' }
      ],
      
      // Expanded sections state
      expandedSections: {
        productType: true,
        brand: false,
        os: false,
        cpu: false,
        ram: false,
        ssd: false,
        weight: false,
        display: false,
        power: false,
        price: false
      },
      
      // Filters object to store selected values
      filters: {
        productType: [],
        brand: [],
        os: [],
        cpu: [],
        ram: [],
        ssd: [],
        weight: [],
        display: [],
        power: [],
        price: []
      },
      activeFilter: 'all',
      expandedSections: {
        productType: true,
        brand: true,
        os: true,
        cpu: true,
        ram: true,
        ssd: true,
        weight: true,
        display: true,
        power: true,
        price: true
      },
      filters: {
        productType: [],
        brand: [],
        os: [],
        cpu: [],
        ram: [],
        ssd: [],
        weight: [],
        display: [],
        power: [],
        price: []
      },
      productTypeOptions: [
        { label: 'Laptops', value: 'laptops' },
        { label: 'Desktops', value: 'desktops' },
        { label: 'All in One', value: 'all-in-one' },
        { label: 'Others', value: 'others' }
      ],
      brandOptions: [
        { label: 'Apple', value: 'apple' },
        { label: 'Samsung', value: 'samsung' },
        { label: 'Others', value: 'others' }
      ],
      osOptions: [
        { label: 'Mac', value: 'mac' },
        { label: 'Windows', value: 'windows' },
        { label: 'Others', value: 'others' }
      ],
      cpuOptions: [
        { label: 'i3', value: 'i3' },
        { label: 'i5', value: 'i5' },
        { label: 'i7', value: 'i7' },
        { label: 'i9', value: 'i9' },
        { label: '3', value: '3' },
        { label: '5', value: '5' },
        { label: '7', value: '7' },
        { label: '9', value: '9' },
        { label: 'Others', value: 'others' }
      ],
      ramOptions: [
        { label: '4GB', value: '4' },
        { label: '8GB', value: '8' },
        { label: '16GB', value: '16' },
        { label: '32GB', value: '32' },
        { label: '64GB', value: '64' },
        { label: 'Others', value: 'others' }
      ],
      ssdOptions: [
        { label: '128GB', value: '128' },
        { label: '256GB', value: '256' },
        { label: '512GB', value: '512' },
        { label: '1TB', value: '1024' },
        { label: 'Others', value: 'others' }
      ],
      weightOptions: [
        { label: '~1kg', value: '0-1' },
        { label: '~2kg', value: '1-2' },
        { label: '~3kg', value: '2-3' },
        { label: '3kg~', value: '3+' }
      ],
      displayOptions: [
        { label: '13inch', value: '13' },
        { label: '15inch', value: '15' },
        { label: '24inch', value: '24' },
        { label: '27inch', value: '27' },
        { label: 'Others', value: 'others' }
      ],
      powerOptions: [
        { label: '500~600W', value: '500-600' },
        { label: '650~750W', value: '650-750' },
        { label: '850W~', value: '850+' }
      ],
      priceOptions: [
        { label: '~100만원', value: '0-100' },
        { label: '~200만원', value: '100-200' },
        { label: '200만원~', value: '200+' }
      ]
    }
  },
  methods: {
    toggleSection(section) {
      this.expandedSections[section] = !this.expandedSections[section];
    },
    
    resetFilters() {
      // Reset all filters to empty arrays
      Object.keys(this.filters).forEach(key => {
        this.filters[key] = [];
      });
      
      // Close all sections except the first one
      Object.keys(this.expandedSections).forEach((key, index) => {
        this.expandedSections[key] = index === 0; // Only keep first section open
      });
    },
    
    formatPrice(price) {
      if (!price) return '가격 문의';
      return new Intl.NumberFormat('ko-KR').format(price);
    },
    
    addToCompare(product) {
      // Add to compare functionality
      console.log('Added to compare:', product);
      // You can implement a toast notification here
    },
    
    addToCart(product) {
      // Add to cart functionality
      console.log('Added to cart:', product);
      // You can implement a toast notification here
    },
    
    async performSearch() {
      if (!this.searchQuery.trim()) return;
      
      this.isLoading = true;
      this.searchPerformed = true;
      
      // Update URL with search query
      this.$router.push({ query: { ...this.$route.query, q: this.searchQuery } });
      
      try {
        // Simulate API call with timeout
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Mock data - replace with actual API call
        const mockProducts = [
          {
            id: 1,
            title: 'LG 그램 16인치 최신형',
            brand: 'LG',
            cpu: 'i7-1260P',
            ram: 16,
            ssd: 512,
            price: 1690000,
            originalPrice: 1890000,
            discount: 11,
            isNew: true,
            image: 'https://images.unsplash.com/photo-1593642702821-8a0e0b1d2b5f?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
          },
          {
            id: 2,
            title: '삼성 갤럭시북2 프로 360',
            brand: 'SAMSUNG',
            cpu: 'i5-1240P',
            ram: 8,
            ssd: 256,
            price: 1290000,
            isNew: true,
            image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
          },
          {
            id: 3,
            title: '맥북 에어 M2',
            brand: 'APPLE',
            cpu: 'M2',
            ram: 8,
            ssd: 256,
            price: 1690000,
            image: 'https://images.unsplash.com/photo-1611186871348-b1ce696e5c09?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
          },
          {
            id: 4,
            title: 'LG 울트라PC 15U70Q',
            brand: 'LG',
            cpu: 'i5-1235U',
            ram: 16,
            ssd: 512,
            price: 1390000,
            discount: 7,
            image: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
          },
          {
            id: 5,
            title: '삼성 갤럭시북2 15.6인치',
            brand: 'SAMSUNG',
            cpu: 'i7-1255U',
            ram: 16,
            ssd: 512,
            price: 1590000,
            originalPrice: 1790000,
            discount: 11,
            image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
          },
          {
            id: 6,
            title: '맥북 프로 14인치 M2 Pro',
            brand: 'APPLE',
            cpu: 'M2 Pro',
            ram: 16,
            ssd: 512,
            price: 2690000,
            image: 'https://images.unsplash.com/photo-1611186871348-b1ce696e5c09?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
          }
        ];
        
        // Filter by search query
        this.searchResults = mockProducts.filter(item => 
          item.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          item.brand.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
        
        // Apply filters if any
        this.applyFilters();
        
      } catch (error) {
        console.error('검색 중 오류가 발생했습니다:', error);
        this.searchResults = [];
      } finally {
        this.isLoading = false;
      }
    },
    
    applyFilters() {
      if (!this.searchResults) return;
      
      // Apply each filter if they have values
      Object.entries(this.filters).forEach(([key, values]) => {
        if (values && values.length > 0) {
          this.searchResults = this.searchResults.filter(product => {
            // Handle special cases for numeric ranges
            if (key === 'price') {
              return values.some(range => {
                const [min, max] = range.split('-').map(Number);
                if (max) {
                  return product.price >= min * 10000 && product.price <= max * 10000;
                } else {
                  return product.price >= min * 10000;
                }
              });
            }
            
            // For other filters, check if the product has the selected value
            return values.some(value => 
              String(product[key] || '').toLowerCase() === value.toLowerCase()
            );
          });
        }
      });
    },
    
    setActiveFilter(filter) {
      this.activeFilter = filter;
      if (this.searchQuery) {
        this.performSearch();
      }
    }
  },
  watch: {
    '$route.query': {
      immediate: true,
      handler(newQuery) {
        if (newQuery.q) {
          this.searchQuery = newQuery.q;
          this.performSearch();
        }
      }
    }
  }
}
</script>

<style scoped>
/* Filter section styles */
.filter-section {
  margin-bottom: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #fff;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.filter-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1f2937;
}

.reset-filters {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.reset-filters:hover {
  background-color: #f3f4f6;
}

.filter-title {
  padding: 0.75rem 1rem;
  background-color: #f9fafb;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #374151;
  transition: all 0.2s;
  user-select: none;
}

.filter-title:hover {
  background-color: #f3f4f6;
}

.filter-options {
  padding: 0.5rem 1rem 1rem;
  max-height: 300px;
  overflow-y: auto;
  background-color: #fff;
}

.filter-options label {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
  cursor: pointer;
  user-select: none;
  position: relative;
  padding-left: 2rem;
  margin-bottom: 0.25rem;
}

.filter-options input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  height: 1.25rem;
  width: 1.25rem;
  background-color: #fff;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.filter-options label:hover input ~ .checkmark {
  border-color: #9ca3af;
}

.filter-options input:checked ~ .checkmark {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.checkmark:after {
  content: '';
  position: absolute;
  display: none;
  left: 7px;
  top: 3px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.filter-options input:checked ~ .checkmark:after {
  display: block;
}

.option-label {
  color: #4b5563;
  font-size: 0.9375rem;
  transition: color 0.2s;
}

.filter-options label:hover .option-label {
  color: #1f2937;
}

/* CPU specific styles */
.subtitle {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0.75rem 0 0.5rem;
  font-weight: 500;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.checkbox-group label {
  margin: 0;
  padding: 0.375rem 0.5rem 0.375rem 1.75rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.checkbox-group label:hover {
  background-color: #f3f4f6;
}

/* Scrollbar styling */
.filter-options::-webkit-scrollbar {
  width: 6px;
}

.filter-options::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.filter-options::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.filter-options::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .filter-options {
    max-height: 200px;
  }
  
  .checkbox-group {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .filter-title {
    padding: 0.625rem 0.875rem;
    font-size: 0.9375rem;
  }
  
  .option-label {
    font-size: 0.875rem;
  }
}

/* Animation for chevron */
.filter-title i {
  transition: transform 0.2s ease;
}

.filter-title[aria-expanded="true"] i {
  transform: rotate(180deg);
}

/* Focus styles for accessibility */
.filter-title:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.filter-options input[type="checkbox"]:focus + .checkmark {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}
/* Base styles */
:root {
  --primary-color: #3b82f6;
  --primary-hover: #2563eb;
  --text-primary: #1f2937;
  --text-secondary: #4b5563;
  --border-color: #e5e7eb;
  --bg-gray: #f9fafb;
  --white: #ffffff;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --transition: all 0.2s ease-in-out;
}

/* Base layout */
.search-page {
  background-color: var(--bg-gray);
  min-height: 100vh;
  padding: 2rem 0;
}

.search-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Header styles */
.page-header {
  margin-bottom: 2rem;
  text-align: center;
}

.header-content {
  margin-bottom: 2rem;
}

.header-text .title {
  font-size: 2.25rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.header-text .title span {
  color: var(--primary-color);
}

.header-text .subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

/* Search bar */
.search-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.search-bar {
  display: flex;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: var(--transition);
}

.search-bar:focus-within {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.search-input {
  flex: 1;
  padding: 0.875rem 1.25rem;
  border: 1px solid var(--border-color);
  border-right: none;
  border-radius: var(--radius-lg) 0 0 var(--radius-lg);
  font-size: 1rem;
  transition: var(--transition);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.search-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0 1.5rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: var(--transition);
}

.search-button:hover {
  background-color: var(--primary-hover);
}

/* Search layout */
.search-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

/* Filter sidebar */
.filter-sidebar {
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  height: fit-content;
  position: sticky;
  top: 1rem;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.filter-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.reset-filters {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-md);
  transition: var(--transition);
}

.reset-filters:hover {
  background-color: rgba(59, 130, 246, 0.1);
}

.filter-section {
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1.5rem;
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
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  padding: 0.25rem 0;
}

.filter-title i {
  font-size: 0.75rem;
  color: var(--text-secondary);
  transition: var(--transition);
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.filter-options label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9375rem;
  color: var(--text-secondary);
  position: relative;
  padding-left: 1.75rem;
  min-height: 1.25rem;
}

.filter-options input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  left: 0;
  height: 1.125rem;
  width: 1.125rem;
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: 0.25rem;
  transition: var(--transition);
}

.filter-options label:hover input ~ .checkmark {
  border-color: var(--primary-color);
}

.filter-options input:checked ~ .checkmark {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 6px;
  top: 2px;
  width: 4px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.filter-options input:checked ~ .checkmark:after {
  display: block;
}

/* Search content */
.search-content {
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-sm);
}

/* State containers */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.state-container h3 {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin: 1rem 0 0.5rem;
}

.state-container p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.state-container ul {
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
  padding: 0;
  list-style: none;
}

.state-container li {
  padding: 0.5rem 0;
  color: var(--text-secondary);
  position: relative;
  padding-left: 1.5rem;
}

.state-container li:before {
  content: "•";
  color: var(--primary-color);
  font-weight: bold;
  position: absolute;
  left: 0;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.8;
}

/* Loading spinner */
.custom-loader {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f5f9;
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Results header */
.results-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.results-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem;
}

.results-count {
  color: var(--text-secondary);
  font-size: 0.9375rem;
}

/* Product grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.product-card {
  background: var(--white);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: var(--transition);
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.product-image {
  position: relative;
  padding-top: 75%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #f9fafb;
}

.product-badges {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  display: flex;
  gap: 0.5rem;
}

.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  color: white;
}

.badge.new {
  background-color: #10b981;
}

.badge.discount {
  background-color: #ef4444;
}

.product-info {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.product-brand {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}

.product-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 3.15rem;
}

.product-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.product-specs span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background-color: var(--bg-gray);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.product-specs i {
  color: var(--primary-color);
  font-size: 0.75rem;
}

.product-price {
  margin-top: auto;
  margin-bottom: 1rem;
}

.current-price {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-right: 0.5rem;
}

.original-price {
  font-size: 0.875rem;
  color: #9ca3af;
  text-decoration: line-through;
}

.product-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.btn-compare,
.btn-cart {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-compare {
  background-color: var(--white);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-compare:hover {
  background-color: #f3f4f6;
  border-color: #d1d5db;
}

.btn-cart {
  background-color: var(--primary-color);
  border: 1px solid var(--primary-color);
  color: white;
}

.btn-cart:hover {
  background-color: var(--primary-hover);
  border-color: var(--primary-hover);
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .search-layout {
    grid-template-columns: 240px 1fr;
  }
  
  .product-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 768px) {
  .search-layout {
    grid-template-columns: 1fr;
  }
  
  .filter-sidebar {
    position: static;
    margin-bottom: 1.5rem;
  }
  
  .product-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@media (max-width: 480px) {
  .search-container {
    padding: 0 1rem;
  }
  
  .header-text .title {
    font-size: 1.75rem;
  }
  
  .header-text .subtitle {
    font-size: 1rem;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .search-input {
    border-radius: var(--radius-md) var(--radius-md) 0 0;
    border-right: 1px solid var(--border-color);
    padding: 0.75rem 1rem;
  }
  
  .search-button {
    border-radius: 0 0 var(--radius-md) var(--radius-md);
    padding: 0.75rem;
    justify-content: center;
  }
  
  .product-actions {
    flex-direction: column;
  }
  
  .btn-compare,
  .btn-cart {
    width: 100%;
  }
}

.search-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  min-height: 70vh;
}

.search-layout {
  display: flex;
  gap: 2rem;
  margin-top: 2rem;
}

.filter-sidebar {
  width: 280px;
  flex-shrink: 0;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  height: fit-content;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.filter-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.filter-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

.filter-options {
  margin-bottom: 0.5rem;
}

.filter-options label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  color: #495057;
  transition: color 0.2s;
}

.filter-options label:hover {
  color: #007bff;
}

.filter-options input[type="checkbox"] {
  margin-right: 0.5rem;
  width: 1rem;
  height: 1rem;
}

.search-content {
  flex: 1;
  min-width: 0;
}

.search-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.search-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.search-subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.search-container {
  max-width: 800px;
  margin: 0 auto 3rem;
}

.search-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.search-input {
  flex: 1;
  padding: 0.9rem 1.25rem;
  font-size: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.search-input:focus {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.search-button {
  padding: 0 1.75rem;
  background-color: #4a6cf7;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s, transform 0.1s;
}

.search-button:hover {
  background-color: #3a5bd9;
}

.search-button:active {
  transform: translateY(1px);
}

.search-filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}

.filter-button {
  padding: 0.5rem 1rem;
  background: #f5f7fa;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.filter-button:hover {
  background: #eef1f7;
}

.filter-button.active {
  background-color: #4a6cf7;
  color: white;
  border-color: #4a6cf7;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  color: #7f8c8d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4a6cf7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.results-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0;
}

.results-count {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.result-card {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.result-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.result-image {
  height: 180px;
  background-size: cover;
  background-position: center;
  background-color: #f5f7fa;
}

.result-content {
  padding: 1.25rem;
}

.result-title {
  font-size: 1.1rem;
  margin: 0 0 0.5rem;
  color: #2c3e50;
}

.result-description {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #95a5a6;
}

.result-category {
  background: #f0f4f8;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #4a6cf7;
  font-weight: 500;
}

.no-results, .search-tips {
  text-align: center;
  padding: 4rem 1rem;
  color: #7f8c8d;
}

.no-results i {
  font-size: 3rem;
  color: #bdc3c7;
  margin-bottom: 1rem;
  display: block;
}

.no-results h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.search-tips h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.search-tips ul {
  list-style: none;
  padding: 0;
  max-width: 400px;
  margin: 0 auto;
  text-align: left;
}

.search-tips li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.search-tips li:last-child {
  border-bottom: none;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .search-title {
    font-size: 2rem;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .search-button {
    width: 100%;
    justify-content: center;
    padding: 0.9rem;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
