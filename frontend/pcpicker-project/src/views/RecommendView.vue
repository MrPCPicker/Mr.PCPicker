<template>
  <div class="recommend-page">
    <section class="recommend-hero">
      <div class="recommend-inner">
        <!-- 왼쪽: 추천 컴퓨터 카드 리스트 (최대 3개) -->
        <div class="left-column">
          <h2 class="left-title">Recommended computers for you</h2>

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
                  :src="getThumbSrc(item, index)"
                  :alt="item.title || '추천 컴퓨터 목업 이미지'"
                />
                <div class="price-tag">{{ formatPrice(item.price) }}</div>
              </div>

              <div class="product-body">
                <h3 class="product-title">
                  <a
                    v-if="item.shoppingUrl"
                    class="product-link"
                    :href="item.shoppingUrl"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {{ item.title }}
                  </a>
                  <span v-else>{{ item.title }}</span>
                </h3>
                <ul class="product-specs">
                  <li v-for="(spec, sIdx) in (item.specs || [])" :key="sIdx">
                    {{ spec }}
                  </li>
                </ul>
              </div>

              <button
                class="plus-badge"
                :class="{ 'in-cart': isSelected(item.id) }"
                @click="handlePlusClick(item, index)"
                :aria-pressed="isSelected(item.id)"
              >
                {{ isSelected(item.id) ? '-' : '+' }}
              </button>
            </article>

            <p v-if="!topThree.length" class="state-text">
              조건에 맞는 추천 결과가 없습니다.
            </p>
          </template>
        </div>

        <!-- 오른쪽: GMS 요약 + 요구사항 편집 영역 -->
        <div class="right-column">
          <div class="summary-bubble">
            <textarea
              v-model="editableQuery"
              class="summary-input"
              @keydown.enter="handleQueryEnter"
              aria-label="Edit your requirements"
            ></textarea>
          </div>

          <div class="detail-section">
            <template v-if="loading">
              <div class="loader-wrap">
                <div class="spinner"></div>
                <p class="loading-text">
                  요구사항을 분석하고 맞는 컴퓨터를 찾는 중입니다...
                </p>
              </div>
            </template>

            <template v-else>
              <h4>Needs</h4>
              <ul>
                <li v-for="(need, nIdx) in needsList" :key="'need-' + nIdx">
                  {{ need }}
                </li>
              </ul>

              <h4>Recommend</h4>
              <ul>
                <li v-for="(rec, rIdx) in recommendList" :key="'rec-' + rIdx">
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

    <!-- 🔹 회원가입 모달 -->
    <RegisterModal
      v-if="showRegisterModal"
      @close="closeRegisterModal"
      @registered="handleRegistered"
      @open-login="openLoginFromRegister"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchComputerRecommendations } from "@/services/gmsService";
import AuthService from "@/services/AuthService";
import LoginModal from "@/components/LoginModal.vue";
import RegisterModal from "@/components/RegisterModal.vue";

const CART_STORAGE_KEY = "mrpcpicker_cart";
const RECOMMEND_QUERY_STORAGE_KEY = "mrpcpicker_recommend_query";

export default {
  name: "RecommendView",
  components: {
    LoginModal,
    RegisterModal,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();

    const mockImages = [
      "https://www.nvidia.com/content/dam/en-zz/Solutions/geforce/laptops/geforce-rtx-50-series-laptops-learn-og-1200x630-new.jpg",
      "https://www.nvidia.com/content/nvidiaGDC/gb/en_GB/geforce/laptops/_jcr_content/root/responsivegrid/nv_container/nv_container_454467679/nv_teaser_copy.coreimg.100.1070.jpeg/1737972531775/geforce-rtx-30-series-laptops-ari.jpeg",
      "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4kjRPi9UekiErQNI9YLi_R21z5-iFYaey4w&s",
    ];

    const getThumbSrc = (item, index) => {
      if (item && item.imageUrl) return item.imageUrl;
      return mockImages[index % mockImages.length];
    };

    const query = ref(route.query.q || "");
    const editableQuery = ref(query.value);

    const loadSavedQuery = () => {
      try {
        const saved = (localStorage.getItem(RECOMMEND_QUERY_STORAGE_KEY) || "").trim();
        if (!saved) return "";
        return saved;
      } catch (e) {
        return "";
      }
    };

    const saveQuery = (val) => {
      try {
        const v = (val || "").trim();
        if (!v) return;
        localStorage.setItem(RECOMMEND_QUERY_STORAGE_KEY, v);
      } catch (e) {
        // ignore
      }
    };

    const loading = ref(false);
    const error = ref(null);

    const results = ref([]);
    const needs = ref([]);
    const summary = ref("");
    const recommends = ref([]);

    const isAuthenticated = ref(!!AuthService.getCurrentUser());

    const cart = ref([]);
    const selectedIds = ref([]);

    const showLoginModal = ref(false);
    const showRegisterModal = ref(false);

    const updateAuthState = () => {
      isAuthenticated.value = !!AuthService.getCurrentUser();
    };

    const loadCartFromStorage = () => {
      try {
        const raw = localStorage.getItem(CART_STORAGE_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) cart.value = parsed;
      } catch (e) {
        console.warn("[CART] Failed to parse cart from storage:", e);
      }
    };

    const saveCartToStorage = () => {
      try {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart.value));
      } catch (e) {
        console.warn("[CART] Failed to save cart to storage:", e);
      }
    };

    const isSelected = (id) => {
      if (!id) return false;
      // Check both selectedIds and wishlist in localStorage
      const wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
      return selectedIds.value.includes(id) || wishlist.some(item => item.id === id);
    };

    const isInCart = (id) => {
      if (!id) return false;
      return cart.value.some((item) => item.id === id);
    };

    const toggleSelectionAndCart = (item) => {
      if (!item || !item.id) return;
      const id = item.id;

      if (isSelected(id)) {
        selectedIds.value = selectedIds.value.filter((x) => x !== id);
        cart.value = cart.value.filter((c) => c.id !== id);
      } else {
        selectedIds.value.push(id);
        if (!isInCart(id)) {
          cart.value.push({
            id: item.id,
            title: item.title,
            price: item.price,
            imageUrl: item.imageUrl,
            specs: item.specs || [],
          });
        }
      }

      saveCartToStorage();
    };

    const handlePlusClick = (item, index) => {
      if (!isAuthenticated.value) {
        showRegisterModal.value = false;
        showLoginModal.value = true;
        return;
      }
      
      const wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
      const existingItemIndex = wishlist.findIndex(wishlistItem => wishlistItem.id === item.id);
      
      if (existingItemIndex === -1) {
        // Add to wishlist
        const wishlistItem = {
          id: item.id,
          name: item.title,
          price: item.price,
          quantity: 1,
          image: getThumbSrc(item, index),
          specs: item.specs || []
        };
        wishlist.push(wishlistItem);
        selectedIds.value.push(item.id);
        localStorage.setItem('wishlist', JSON.stringify(wishlist));
        window.dispatchEvent(new Event('storage'));
        window.dispatchEvent(new Event('wishlist-updated'));
        alert(`${item.title}이(가) 찜 목록에 추가되었습니다.`);
      } else {
        // Remove from wishlist
        wishlist.splice(existingItemIndex, 1);
        selectedIds.value = selectedIds.value.filter(id => id !== item.id);
        localStorage.setItem('wishlist', JSON.stringify(wishlist));
        window.dispatchEvent(new Event('storage'));
        window.dispatchEvent(new Event('wishlist-updated'));
        alert(`${item.title}이(가) 찜 목록에서 제거되었습니다.`);
      }
    };

    const closeLoginModal = () => {
      showLoginModal.value = false;
    };

    const closeRegisterModal = () => {
      showRegisterModal.value = false;
    };

    const openRegisterFromLogin = () => {
      showLoginModal.value = false;
      showRegisterModal.value = true;
    };

    const openLoginFromRegister = () => {
      showRegisterModal.value = false;
      showLoginModal.value = true;
    };

    const handleLoggedIn = () => {
      updateAuthState();
      showLoginModal.value = false;
    };

    const handleRegistered = () => {
      updateAuthState();
      showRegisterModal.value = false;
    };

    const topThree = computed(() => results.value.slice(0, 3));
    const needsList = computed(() => needs.value || []);
    const recommendList = computed(() => recommends.value || []);

    const loadRecommendations = async () => {
      if (!query.value) return;

      saveQuery(query.value);

      loading.value = true;
      error.value = null;

      try {
        const data = await fetchComputerRecommendations(query.value);
        if (!data) return;

        results.value = data.results || [];
        needs.value = data.needs || [];
        summary.value = data.summary || "";
        recommends.value = data.recommends || [];
        selectedIds.value = [];
      } catch (err) {
        console.error("추천 호출 실패:", err);
        error.value = err;
      } finally {
        loading.value = false;
      }
    };

    const rewriteSearch = async () => {
      const nextQuery = (editableQuery.value || "").trim();
      if (!nextQuery || loading.value) return;

      query.value = nextQuery;

      saveQuery(nextQuery);
      try {
        await router.replace({
          name: "Recommend",
          query: { ...route.query, q: nextQuery },
        });
      } catch (e) {
        // ignore
      }
      await loadRecommendations();
    };

    const handleQueryEnter = async (e) => {
      if (!e) return;
      if (e.shiftKey) return;
      e.preventDefault();
      await rewriteSearch();
    };

    const formatPrice = (price) => {
      if (price === null || price === undefined || price === "") {
        return "가격 정보 없음";
      }
      const num = Number(price);
      if (Number.isNaN(num)) return price;
      return new Intl.NumberFormat("ko-KR", {
        style: "currency",
        currency: "KRW",
        maximumFractionDigits: 0,
      }).format(num);
    };

    onMounted(() => {
      window.addEventListener("auth-changed", updateAuthState);
      loadCartFromStorage(); // Load cart state when component mounts

      const saved = loadSavedQuery();
      const routeQ = (route.query.q || "").toString().trim();
      const initial = routeQ || saved;
      if (initial) {
        query.value = initial;
        editableQuery.value = initial;
        saveQuery(initial);
      }

      loadCartFromStorage();
      loadRecommendations();
    });

    onUnmounted(() => {
      window.removeEventListener("auth-changed", updateAuthState);
    });

    watch(editableQuery, (v) => {
      saveQuery(v);
    });

    watch(
      () => [route.query.q, route.query.ts],
      async ([nextQ]) => {
        const q = (nextQ || "").toString().trim();
        if (!q) return;

        query.value = q;
        editableQuery.value = q;
        saveQuery(q);
        await loadRecommendations();
      }
    );

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
      handleQueryEnter,
      formatPrice,
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
      getThumbSrc,
    };
  },
};
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
  overflow: hidden;
}

.product-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.price-tag {
  position: absolute;
  bottom: 16px;
  right: 18px;
  font-size: 13px;
  font-weight: 700;
  color: #4b4b63;
}

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

.product-link {
  color: inherit;
  text-decoration: underline;
}

.product-link:hover {
  opacity: 0.9;
}

.product-specs {
  list-style: disc;
  padding-left: 20px;
  font-size: 14px;
  color: #cfd5ff;
}

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
