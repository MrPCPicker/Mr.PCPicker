<template>
  <div class="product-card" @click="goToDetail">
    <div class="image-container">
      <img
        :src="productImage"
        :alt="product.name || '상품 이미지'"
        class="product-image"
        @error="handleImageError"
      />
    </div>

    <div class="product-body">
      <div class="brand">{{ product.brand || '브랜드 정보 없음' }}</div>

      <h3 class="title">
        {{ product.name || product.title || '상품명 정보 없음' }}
      </h3>

      <div class="specs">
        <span v-if="product.cpu"><i class="fas fa-microchip"></i> {{ product.cpu }}</span>
        <span v-if="product.ram"><i class="fas fa-memory"></i> {{ product.ram }}GB</span>
        <span v-if="product.ssd"><i class="fas fa-hdd"></i> {{ product.ssd }}GB</span>
      </div>

      <div class="price">
        {{ formatPrice(product.price) }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProductCard',
  props: {
    product: {
      type: Object,
      required: true,
      default: () => ({
        id: null,
        name: '',
        brand: '',
        price: 0,
        image: '',
        stock: 0,
        cpu: '',
        ram: 0,
        ssd: 0
      })
    }
  },
  data() {
    return {
      imageError: false
    }
  },
  computed: {
    productImage() {
      if (this.imageError || !this.product.image) {
        return 'https://via.placeholder.com/300x200?text=No+Image';
      }
      return this.product.image.startsWith('http') ? this.product.image : 
             `${process.env.VUE_APP_API_URL || ''}${this.product.image}`;
    }
  },
  methods: {
    formatPrice(price) {
      if (price === undefined || price === null) return '가격 문의';
      return new Intl.NumberFormat('ko-KR').format(price) + '원';
    },
    handleImageError() {
      this.imageError = true;
    },
    goToDetail() {
      if (this.product.id) {
        this.$router.push(`/products/${this.product.id}`);
      }
    }
  }
}
</script>

<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>

<style scoped>
.product-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  border-color: #3b82f6;
}

.image-container {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 1rem;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

.product-body {
  padding: 1.25rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.brand {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0.5rem 0;
  color: #1f2937;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 3em;
  line-height: 1.5;
}

.specs {
  font-size: 0.8rem;
  color: #4b5563;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin: 0.5rem 0;
  flex-grow: 1;
}

.specs span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.specs i {
  color: #6b7280;
  width: 16px;
  text-align: center;
}

.price {
  margin-top: 0.75rem;
  font-weight: bold;
  font-size: 1.1rem;
  color: #1e40af;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock {
  font-size: 0.8rem;
  font-weight: normal;
  color: #10b981;
  background: #ecfdf5;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
}

.stock.out-of-stock {
  color: #ef4444;
  background: #fef2f2;
}

@media (max-width: 768px) {
  .image-container {
    height: 160px;
  }
  
  .product-body {
    padding: 1rem;
  }
  
  .title {
    font-size: 0.95rem;
  }
  
  .price {
    font-size: 1rem;
  }
}
</style>
