<template>
  <div class="recommend-page">
    <!-- Toast Notification -->
    <div v-if="toast.show" class="toast" :class="{ 'toast-success': !toast.isError, 'toast-error': toast.isError }">
      {{ toast.message }}
    </div>
    
    <section class="recommend-hero">
      <div class="recommend-inner">
        <!-- 왼쪽: 추천 컴퓨터 카드 리스트 -->
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
                  :alt="item.title || '추천 컴퓨터 이미지'"
                />
                <div class="thumb-overlay"></div>
                <div class="price-tag">{{ formatPrice(item) }}</div>
              </div>

              <div class="product-body">
                <h3 class="product-title">
                  <a
                    v-if="item.shoppingUrl"
                    :href="item.shoppingUrl"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="product-link"
                  >
                    {{ item.title }}
                  </a>
                  <span v-else>{{ item.title }}</span>
                </h3>

                <!-- ✅ GPU 문자열(dict) 가독성 처리 -->
                <ul class="product-specs">
                  <li
                    v-for="(spec, sIdx) in (item.specs || [])"
                    :key="sIdx"
                  >
                    <template
                      v-if="typeof spec === 'string' && spec.startsWith('GPU:')"
                    >
                      {{ formatGpuSpecFromString(spec) }}
                    </template>
                    <template v-else>
                      {{ spec }}
                    </template>
                  </li>
                </ul>
              </div>

              <button
                class="plus-badge"
                :class="{ 'in-cart': isSelected(item.id) }"
                @click="handlePlusClick(item)"
              >
                {{ isSelected(item.id) ? "-" : "+" }}
              </button>
            </article>

            <p v-if="!topThree.length" class="state-text">
              조건에 맞는 추천 결과가 없습니다.
            </p>
          </template>
        </div>

        <!-- 오른쪽 요약 -->
        <div class="right-column">
          <div class="summary-bubble">
            <textarea
              v-model="editableQuery"
              class="summary-input"
              @keydown.enter="handleQueryEnter"
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

            <template v-else-if="!error">
              <h4>Needs</h4>
              <ul>
                <li v-for="(n, i) in needsList" :key="i">{{ n }}</li>
              </ul>

              <h4>Recommend</h4>
              <ul>
                <li v-for="(r, i) in recommendList" :key="i">{{ r }}</li>
              </ul>
            </template>
          </div>

          <div class="rewrite-area">
            <button
              class="rewrite-btn"
              @click="rewriteSearch"
              :disabled="loading"
            >
              {{ loading ? "Loading..." : "Rewrite" }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <LoginModal v-if="showLoginModal" @close="showLoginModal = false" />
    <RegisterModal v-if="showRegisterModal" @close="showRegisterModal = false" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchComputerRecommendations } from "@/services/gmsService";
import AuthService from "@/services/AuthService";
import LoginModal from "@/components/LoginModal.vue";
import RegisterModal from "@/components/RegisterModal.vue";

export default {
  name: "RecommendView",
  components: { LoginModal, RegisterModal },

  setup() {
    const route = useRoute();
    const router = useRouter();

    const query = ref(route.query.q || "");
    const editableQuery = ref(query.value);

    const loading = ref(false);
    const error = ref(null);

    const results = ref([]);
    const needs = ref([]);
    const recommends = ref([]);

    const selectedIds = ref([]);
    const isAuthenticated = ref(!!AuthService.getCurrentUser());

    const showLoginModal = ref(false);
    const showRegisterModal = ref(false);
    
    // Toast notification
    const toast = ref({
      show: false,
      message: '',
      isError: false
    });
    
    const showToast = (message, isError = false) => {
      toast.value = {
        show: true,
        message,
        isError
      };
      
      setTimeout(() => {
        toast.value.show = false;
      }, 3000);
    };

    const mockImages = [
      "https://www.nvidia.com/content/dam/en-zz/Solutions/geforce/laptops/geforce-rtx-50-series-laptops-learn-og-1200x630-new.jpg",
      "https://www.nvidia.com/content/nvidiaGDC/gb/en_GB/geforce/laptops/_jcr_content/root/responsivegrid/nv_container/nv_container_454467679/nv_teaser_copy.coreimg.100.1070.jpeg/1737972531775/geforce-rtx-30-series-laptops-ari.jpeg",
      "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4kjRPi9UekiErQNI9YLi_R21z5-iFYaey4w&s",
    ];

    const getThumbSrc = (item, index) =>
      item?.imageUrl || mockImages[index % mockImages.length];

    const topThree = computed(() => results.value.slice(0, 3));
    const needsList = computed(() => needs.value || []);
    const recommendList = computed(() => recommends.value || []);

    /* ✅ 핵심: GPU 문자열(dict) 파싱 */
    const formatGpuSpecFromString = (spec) => {
      if (!spec.startsWith("GPU:")) return spec;

      const raw = spec.replace("GPU:", "").trim();
      if (!raw.startsWith("{") || !raw.endsWith("}")) return spec;

      const body = raw.slice(1, -1);
      const parts = body.split(",").map((p) => p.trim());

      const cleaned = parts
        .map((p) => {
          const [key, value] = p.split(":");
          if (!key || !value) return null;

          const readableKey = key
            .replace(/['"]/g, "")
            .replace(/_/g, " ")
            .replace(/([A-Z])/g, " $1")
            .trim();

          const readableValue = value.replace(/['"]/g, "").trim();
          if (!readableValue) return null;

          return `${readableKey}: ${readableValue}`;
        })
        .filter(Boolean);

      return cleaned.length
        ? `GPU: ${cleaned.join(", ")}`
        : "GPU 정보 없음";
    };

    const loadRecommendations = async () => {
      if (!query.value) return;
      loading.value = true;
      error.value = null;

      try {
        const data = await fetchComputerRecommendations(query.value);
        results.value = data.results || [];
        needs.value = data.needs || [];
        recommends.value = data.recommends || [];
        selectedIds.value = [];
      } catch (e) {
        error.value = e;
      } finally {
        loading.value = false;
      }
    };

    const rewriteSearch = async () => {
      if (!editableQuery.value.trim()) return;
      query.value = editableQuery.value.trim();
      await router.replace({ name: "Recommend", query: { q: query.value } });
      await loadRecommendations();
    };

    const handleQueryEnter = async (e) => {
      if (!e.shiftKey) {
        e.preventDefault();
        await rewriteSearch();
      }
    };

    const isSelected = (id) => selectedIds.value.includes(id);

    const handlePlusClick = (item) => {
      if (!isAuthenticated.value) {
        showLoginModal.value = true;
        return;
      }
      
      // Load current wishlist from localStorage
      const currentWishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
      
      if (selectedIds.value.includes(item.id)) {
        // Remove from wishlist
        selectedIds.value = selectedIds.value.filter((i) => i !== item.id);
        const updatedWishlist = currentWishlist.filter((i) => i.id !== item.id);
        localStorage.setItem('wishlist', JSON.stringify(updatedWishlist));
        showToast(`'${item.title}'이(가) 위시리스트에서 제거되었습니다.`);
      } else {
        // Add to wishlist
        selectedIds.value.push(item.id);
        
        // Create a clean item object with only necessary properties
        const wishlistItem = {
          id: item.id,
          title: item.title,
          price: item.priceValue || 0,
          imageUrl: item.imageUrl || mockImages[Math.floor(Math.random() * mockImages.length)],
          specs: item.specs || [],
          shoppingUrl: item.shoppingUrl || ''
        };
        
        const updatedWishlist = [...currentWishlist, wishlistItem];
        localStorage.setItem('wishlist', JSON.stringify(updatedWishlist));
        showToast(`'${item.title}'이(가) 위시리스트에 추가되었습니다.`);
      }
      
      // Trigger wishlist update event for other components
      window.dispatchEvent(new Event('wishlist-updated'));
    };

    const formatPrice = (item) =>
      item?.priceValue
        ? new Intl.NumberFormat("ko-KR", {
            style: "currency",
            currency: "KRW",
            maximumFractionDigits: 0,
          }).format(item.priceValue)
        : item?.price || "가격 정보 없음";

    onMounted(() => {
      loadRecommendations();
      
      // Load wishlist from localStorage when component mounts
      const savedWishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
      selectedIds.value = savedWishlist.map(item => item.id);
    });

    return {
      editableQuery,
      loading,
      error,
      topThree,
      needsList,
      recommendList,
      rewriteSearch,
      handleQueryEnter,
      formatPrice,
      isSelected,
      handlePlusClick,
      showLoginModal,
      showRegisterModal,
      formatGpuSpecFromString,
      getThumbSrc,
      toast,
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

.thumb-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.4) 50%, transparent 100%);
  pointer-events: none;
}

.price-tag {
  position: absolute;
  bottom: 16px;
  right: 18px;
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
  z-index: 1;
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

/* Toast Notification Styles */
.toast {
  position: fixed;
  left: 50%;
  bottom: 30px;
  transform: translateX(-50%);
  background-color: #10b981;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  animation: slideUp 0.3s ease-out;
  font-size: 14px;
  font-weight: 500;
}

.toast-success {
  background-color: #10b981;
}

.toast-error {
  background-color: #ef4444;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translate(-50%, 20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>