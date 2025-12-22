<!-- src/views/RecommendView.vue -->
<template>
  <div class="recommend-page">
    <section class="recommend-hero">
      <div class="recommend-inner">
        <!-- 왼쪽: 추천 노트북 카드 리스트 (최대 3개) -->
        <div class="left-column">
          <h2 class="left-title">Recommended laptops for you</h2>

          <p v-if="loading" class="state-text">추천을 불러오는 중입니다...</p>
          <p v-else-if="error" class="state-text error">
            추천을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.
          </p>

          <template v-else>
            <article
              v-for="(item, index) in topThree"
              :key="item.id || index"
              class="product-card"
            >
              <div class="product-thumb">
                <img
                  v-if="item.imageUrl"
                  :src="item.imageUrl"
                  :alt="item.title"
                />
                <div v-else class="thumb-placeholder">
                  <span class="thumb-icon">💻</span>
                </div>

                <div class="price-tag">
                  {{ formatPrice(item.price) }}
                </div>
              </div>

              <div class="product-body">
                <h3 class="product-title">{{ item.title }}</h3>
                <ul class="product-specs">
                  <li
                    v-for="(spec, sIdx) in (item.specs || [])"
                    :key="sIdx"
                  >
                    {{ spec }}
                  </li>
                </ul>
              </div>

              <!-- 기본은 +, 클릭하면 이 화면 기준으로만 - 토글 -->
              <button
                class="plus-badge"
                :class="{ 'in-cart': isSelected(item.id) }"
                @click="handlePlusClick(item)"
                :aria-pressed="isSelected(item.id)"
              >
                {{ isSelected(item.id) ? '-' : '+' }}
              </button>
            </article>

            <p
              v-if="!topThree.length"
              class="state-text"
            >
              조건에 맞는 추천 결과가 없습니다.
            </p>
          </template>
        </div>

        <!-- 오른쪽: GMS 요약 + 요구사항 편집 영역 -->
        <div class="right-column">
          <!-- 상단: 사용자가 입력했던 요구사항을 그대로 보여주는 textarea -->
          <div class="summary-bubble">
            <textarea
              v-model="editableQuery"
              class="summary-input"
              aria-label="Edit your requirements"
            ></textarea>
          </div>

          <!-- 🔹 로딩 중에는 Needs/Recommend 대신 로딩 애니메이션 표시 -->
          <div class="detail-section">
            <template v-if="loading">
              <div class="loader-wrap">
                <div class="spinner"></div>
                <p class="loading-text">
                  요구사항을 분석하고 맞는 노트북을 찾는 중입니다...
                </p>
              </div>
            </template>

            <template v-else>
              <h4>Needs</h4>
              <ul>
                <li
                  v-for="(need, nIdx) in needsList"
                  :key="'need-' + nIdx"
                >
                  {{ need }}
                </li>
              </ul>

              <h4>Recommend</h4>
              <ul>
                <li
                  v-for="(rec, rIdx) in recommendList"
                  :key="'rec-' + rIdx"
                >
                  {{ rec }}
                </li>
              </ul>
            </template>
          </div>

          <div class="rewrite-area">
            <button
              class="rewrite-btn"
              @click="rewriteSearch"
              :disabled="loading"
            >
              {{ loading ? 'Loading...' : 'Rewrite' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 🔹 로그인 모달 -->
    <LoginModal
      v-if="showLoginModal"
      @close="closeLoginModal"
      @logged-in="handleLoggedIn"
      @open-register="openRegisterFromLogin"
    />

    <!-- 🔹 회원가입 모달 (로그인 모달에서 넘어올 수 있게) -->
    <RegisterModal
      v-if="showRegisterModal"
      @close="closeRegisterModal"
      @registered="handleRegistered"
      @open-login="openLoginFromRegister"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchLaptopRecommendations } from '@/services/gmsService'
import AuthService from '@/services/AuthService'
import LoginModal from '@/components/LoginModal.vue'
import RegisterModal from '@/components/RegisterModal.vue'

const CART_STORAGE_KEY = 'mrpcpicker_cart'

export default {
  name: 'RecommendView',
  components: {
    LoginModal,
    RegisterModal,
  },
  setup() {
    const route = useRoute()

    // 처음에는 SearchBar 에서 넘어온 q 값
    const query = ref(route.query.q || '')
    // 오른쪽 상단 textarea 에서 수정 가능한 값
    const editableQuery = ref(query.value)

    const loading = ref(false)
    const error = ref(null)

    const results = ref([])
    const needs = ref([])
    const summary = ref('')
    const recommends = ref([])

    // 로그인 여부
    const isAuthenticated = ref(!!AuthService.getCurrentUser())

    // 장바구니 (프로필에서 사용할 데이터)
    const cart = ref([]) // [{id, title, price, imageUrl, specs}, ...]
    // 이 Recommend 화면에서 선택된 카드 id (버튼 상태 용)
    const selectedIds = ref([])

    // 모달 상태
    const showLoginModal = ref(false)
    const showRegisterModal = ref(false)

    const updateAuthState = () => {
      isAuthenticated.value = !!AuthService.getCurrentUser()
    }

    // localStorage에서 cart 불러오기
    const loadCartFromStorage = () => {
      try {
        const raw = localStorage.getItem(CART_STORAGE_KEY)
        if (!raw) return
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed)) {
          cart.value = parsed
        }
      } catch (e) {
        console.warn('[CART] Failed to parse cart from storage:', e)
      }
    }

    const saveCartToStorage = () => {
      try {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart.value))
      } catch (e) {
        console.warn('[CART] Failed to save cart to storage:', e)
      }
    }

    // 버튼 상태: 이번 추천 화면에서 선택된 것 기준
    const isSelected = (id) => {
      if (!id) return false
      return selectedIds.value.includes(id)
    }

    // 실제 장바구니 안에 있는지
    const isInCart = (id) => {
      if (!id) return false
      return cart.value.some((item) => item.id === id)
    }

    const toggleSelectionAndCart = (item) => {
      if (!item || !item.id) return
      const id = item.id

      if (isSelected(id)) {
        // 선택 해제: 버튼 - → +, cart에서도 제거
        selectedIds.value = selectedIds.value.filter((x) => x !== id)
        cart.value = cart.value.filter((c) => c.id !== id)
      } else {
        // 선택: 버튼 + → -, cart에 추가 (중복 방지)
        selectedIds.value.push(id)
        if (!isInCart(id)) {
          cart.value.push({
            id: item.id,
            title: item.title,
            price: item.price,
            imageUrl: item.imageUrl,
            specs: item.specs || [],
          })
        }
      }

      saveCartToStorage()
      console.log('[CART] current cart:', cart.value)
    }

    // + 버튼 클릭 시 동작
    const handlePlusClick = (item) => {
      if (!isAuthenticated.value) {
        // 로그인 안 되어 있으면 로그인 모달 오픈
        showRegisterModal.value = false
        showLoginModal.value = true
        return
      }
      // 로그인 되어 있으면 선택 + 장바구니 토글
      toggleSelectionAndCart(item)
    }

    const closeLoginModal = () => {
      showLoginModal.value = false
    }

    const closeRegisterModal = () => {
      showRegisterModal.value = false
    }

    // 로그인 모달 → 회원가입 모달
    const openRegisterFromLogin = () => {
      showLoginModal.value = false
      showRegisterModal.value = true
    }

    // 회원가입 모달 → 로그인 모달
    const openLoginFromRegister = () => {
      showRegisterModal.value = false
      showLoginModal.value = true
    }

    const handleLoggedIn = () => {
      // 모달에서 로그인 성공 시 호출
      updateAuthState()
      showLoginModal.value = false
    }

    const handleRegistered = () => {
      // 회원가입 성공 시 로그인된 상태로 간주
      updateAuthState()
      showRegisterModal.value = false
    }

    const topThree = computed(() => results.value.slice(0, 3))
    const needsList = computed(() => needs.value || [])
    const recommendList = computed(() => recommends.value || [])

    const loadRecommendations = async () => {
      if (!query.value) return

      loading.value = true
      error.value = null

      try {
        const data = await fetchLaptopRecommendations(query.value)
        if (!data) {
          return
        }
        results.value = data.results || []
        needs.value = data.needs || []
        summary.value = data.summary || ''
        recommends.value = data.recommends || []
        // 새 추천이 들어오면 선택 상태 초기화 → 항상 + 로 시작
        selectedIds.value = []
      } catch (err) {
        console.error('추천 호출 실패:', err)
        error.value = err
      } finally {
        loading.value = false
      }
    }

    // Rewrite: 현재 textarea(editableQuery)의 내용으로 다시 GMS 호출
    const rewriteSearch = async () => {
      const nextQuery = (editableQuery.value || '').trim()
      if (!nextQuery || loading.value) return

      query.value = nextQuery
      await loadRecommendations()
    }

    const formatPrice = (price) => {
      if (price === null || price === undefined || price === '') {
        return '가격 정보 없음'
      }
      const num = Number(price)
      if (Number.isNaN(num)) return price
      return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        maximumFractionDigits: 0,
      }).format(num)
    }

    onMounted(() => {
      window.addEventListener('auth-changed', updateAuthState)
      loadCartFromStorage()
      loadRecommendations()
    })

    onUnmounted(() => {
      window.removeEventListener('auth-changed', updateAuthState)
    })

    return {
      query,
      editableQuery,
      loading,
      error,
      results,
      topThree,
      needsList,
      recommendList,
      rewriteSearch,
      formatPrice,
      // auth & cart & modal & selection
      isAuthenticated,
      cart,
      isSelected,
      handlePlusClick,
      showLoginModal,
      showRegisterModal,
      closeLoginModal,
      closeRegisterModal,
      openRegisterFromLogin,
      openLoginFromRegister,
      handleLoggedIn,
      handleRegistered,
    }
  },
}
</script>

<style scoped>
.recommend-page {
  min-height: 100vh;
  background-color: #2f3a45;
  padding-bottom: 80px;
}

.recommend-hero {
  max-width: 1200px;
  margin: 0 auto;
  padding: 96px 48px 40px;
}

.recommend-inner {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 40px;
}

/* 왼쪽 카드 컬럼 */
.left-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.left-title {
  font-size: 24px;
  font-weight: 700;
  color: #f9fafb;
}

.state-text {
  font-size: 14px;
  color: #e5e7eb;
}
.state-text.error {
  color: #fecaca;
}

.product-card {
  position: relative;
  display: grid;
  grid-template-columns: 200px 1fr;
  background: #3a444e;
  border-radius: 28px;
  overflow: hidden;
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
}

.product-thumb {
  position: relative;
  background: #f5f4ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-thumb img {
  max-width: 80%;
  max-height: 80%;
  object-fit: contain;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb-icon {
  font-size: 32px;
}

.price-tag {
  position: absolute;
  bottom: 16px;
  right: 18px;
  font-size: 13px;
  font-weight: 700;
  color: #4b4b63;
}

/* 카드 본문 */
.product-body {
  padding: 20px 28px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #eef1ff;
}

.product-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.product-specs {
  list-style: disc;
  padding-left: 20px;
  font-size: 14px;
  color: #cfd5ff;
}

/* 왼쪽 + / - 버튼 */
.plus-badge {
  position: absolute;
  left: 18px;
  bottom: 18px;
  width: 36px;
  height: 36px;
  border-radius: 999px;
  border: none;
  background: #6b5fcf;
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition:
    background-color 0.2s ease,
    transform 0.1s ease,
    box-shadow 0.2s ease;
}

.plus-badge:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

/* 선택(장바구니 추가)된 상태 */
.plus-badge.in-cart {
  background: #10b981;
}

/* 오른쪽 요약 컬럼 */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
  background: #3b454f;
  border-radius: 32px;
  padding: 32px 32px 24px;
}

/* 상단 textarea 버블 */
.summary-bubble {
  background: #f3f0ff;
  border-radius: 28px;
  padding: 18px 22px;
  min-height: 80px;
  display: flex;
  align-items: center;
}

.summary-input {
  width: 100%;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  font-size: 14px;
  line-height: 1.6;
  color: #4b4b63;
  font-family: 'Inter', 'DM Sans', 'Pretendard', sans-serif;
  white-space: pre-wrap;
  overflow-y: auto;
}

/* Needs / Recommend 섹션 */
.detail-section {
  font-size: 14px;
  color: #e5e7f4;
}

.detail-section h4 {
  font-size: 15px;
  font-weight: 700;
  margin-top: 12px;
  margin-bottom: 4px;
}

.detail-section ul {
  list-style: disc;
  padding-left: 18px;
}

/* 로딩 애니메이션 */
.loader-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.spinner {
  width: 18px;
  height: 18px;
  border-radius: 999px;
  border: 3px solid rgba(255, 255, 255, 0.25);
  border-top-color: #ffffff;
  animation: spin 0.8s linear infinite;
}

.loading-text {
  font-size: 13px;
  color: #e5e7f4;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.rewrite-area {
  display: flex;
  justify-content: flex-end;
  margin-top: auto;
}

.rewrite-btn {
  padding: 10px 26px;
  border-radius: 999px;
  border: none;
  background: #6b5fcf;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.rewrite-btn:disabled {
  opacity: 0.7;
  cursor: default;
}

.rewrite-btn:hover:enabled {
  opacity: 0.9;
}
</style>
