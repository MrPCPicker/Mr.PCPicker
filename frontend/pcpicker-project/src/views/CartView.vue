<template>
  <div class="cart-page">
    <div class="cart-container">
      <h1 class="page-title">장바구니</h1>
      
      <div v-if="cartItems.length === 0" class="empty-cart">
        <i class="fas fa-shopping-cart"></i>
        <p>장바구니가 비어있습니다.</p>
        <router-link to="/" class="browse-btn">쇼핑 계속하기</router-link>
      </div>

      <div v-else>
        <div class="cart-items">
          <div v-for="(item, index) in cartItems" :key="item.id" class="cart-item">
            <img :src="getItemImage(item)" :alt="item.name" class="item-image">
            <div class="item-details">
              <h3>{{ item.name }}</h3>
              <p class="item-price">{{ formatPrice(item.price) }}원</p>
              <div class="quantity-controls">
                <button @click="updateQuantity(index, -1)">-</button>
                <span>{{ item.quantity }}</span>
                <button @click="updateQuantity(index, 1)">+</button>
              </div>
            </div>
            <div class="item-actions">
              <button @click="removeItem(index)" class="remove-btn" title="Remove item">
                <i class="fas fa-times"></i> 삭제
              </button>
            </div>
          </div>
        </div>

        <div class="cart-summary">
          <h3>주문 요약</h3>
          <div class="summary-row">
            <span>상품 가격</span>
            <span>{{ formatPrice(subtotal) }}원</span>
          </div>
          <div class="summary-row">
            <span>배송비</span>
            <span>{{ shippingFee === 0 ? '무료' : formatPrice(shippingFee) + '원' }}</span>
          </div>
          <div class="summary-total">
            <span>총 결제 금액</span>
            <span class="total-amount">{{ formatPrice(total) }}원</span>
          </div>
          <button class="checkout-btn">주문하기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CartView',
  data() {
    return {
      cartItems: JSON.parse(localStorage.getItem('cart')) || [],
      shippingFee: 3000, // 기본 배송비
      freeShippingThreshold: 50000 // 무료 배송 최소 금액
    }
  },
  computed: {
    subtotal() {
      return this.cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    },
    total() {
      return this.subtotal + (this.subtotal >= this.freeShippingThreshold ? 0 : this.shippingFee)
    }
  },
  methods: {
    getItemImage(item) {
      // If the item has an image property, use it
      if (item.image) return item.image;
      // If the item has an imageUrl, use it
      if (item.imageUrl) return item.imageUrl;
      // Fallback to a default image
      return 'https://via.placeholder.com/100';
    },
    formatPrice(price) {
      return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    },
    updateQuantity(index, change) {
      const newQuantity = this.cartItems[index].quantity + change
      if (newQuantity > 0) {
        this.cartItems[index].quantity = newQuantity
        this.saveCart()
      }
    },
    removeItem(index) {
      this.cartItems.splice(index, 1)
      this.saveCart()
    },
    saveCart() {
      localStorage.setItem('cart', JSON.stringify(this.cartItems))
      window.dispatchEvent(new Event('storage')) // Update cart count in navbar
    }
  },
  mounted() {
    // Listen for cart updates from other components
    window.addEventListener('storage', () => {
      this.cartItems = JSON.parse(localStorage.getItem('cart')) || []
    })
  }
}
</script>

<style scoped>
.cart-page {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 30px;
  color: #2f3a45;
}

.empty-cart {
  text-align: center;
  padding: 60px 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.empty-cart i {
  font-size: 48px;
  color: #adb5bd;
  margin-bottom: 20px;
}

.empty-cart p {
  font-size: 18px;
  color: #6c757d;
  margin-bottom: 20px;
}

.browse-btn {
  display: inline-block;
  padding: 12px 24px;
  background-color: #2f3a45;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: background-color 0.2s;
}

.browse-btn:hover {
  background-color: #1e6fd7;
}

.cart-items {
  margin-bottom: 30px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.item-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  margin-right: 20px;
}

.item-details {
  flex: 1;
}

.item-details h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #2f3a45;
}

.item-price {
  font-size: 18px;
  font-weight: 700;
  color: #1e6fd7;
  margin-bottom: 15px;
}

.quantity-controls {
  display: flex;
  align-items: center;
}

.quantity-controls button {
  width: 30px;
  height: 30px;
  border: 1px solid #dee2e6;
  background: white;
  font-size: 16px;
  cursor: pointer;
  border-radius: 4px;
}

.quantity-controls button:hover {
  background: #f8f9fa;
}

.quantity-controls span {
  display: inline-block;
  width: 40px;
  text-align: center;
  font-weight: 500;
}

.remove-btn {
  background: none;
  border: none;
  color: #868e96;
  font-size: 18px;
  cursor: pointer;
  padding: 5px;
  transition: color 0.2s;
}

.item-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.remove-btn {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #6c757d;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #fff5f5;
  color: #fa5252;
  border-color: #ffc9c9;
}

.remove-btn i {
  font-size: 14px;
}

.cart-summary {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.cart-summary h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 18px;
  color: #2f3a45;
  padding-bottom: 15px;
  border-bottom: 1px solid #f1f3f5;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  color: #495057;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px solid #f1f3f5;
  font-size: 18px;
  font-weight: 600;
  color: #2f3a45;
}

.total-amount {
  color: #1e6fd7;
  font-size: 22px;
}

.checkout-btn {
  width: 100%;
  padding: 16px;
  background-color: #1e6fd7;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 20px;
  transition: background-color 0.2s;
}

.checkout-btn:hover {
  background-color: #1a5fb4;
}

@media (max-width: 768px) {
  .cart-item {
    flex-direction: column;
    text-align: center;
  }
  
  .item-image {
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .quantity-controls {
    justify-content: center;
  }
}
</style>
