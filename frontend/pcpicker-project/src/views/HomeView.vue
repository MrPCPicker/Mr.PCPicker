<!-- src/views/HomeView.vue -->
<template>
  <div class="home">
    <!-- 네비게이션은 App.vue의 <Navbar />가 전역으로 담당 -->

    <!-- Hero Section -->
    <main>
      <section class="hero">
        <div class="hero-inner">
          <!-- 왼쪽: 문구 영역 (수직 중앙, 왼쪽 정렬, 이동 없음) -->
          <div class="hero-text">
            <h1 class="hero-title">
              Build the right PC<br />
              for your needs
            </h1>
            <p class="hero-desc">
              스펙 비교부터 추천까지, Mr.PC Picker가<br />
              당신에게 가장 잘 맞는 데스크탑·노트북 구성을 찾아드립니다.
            </p>
          </div>

          <!-- 오른쪽: SearchBar 영역 (수직 중앙, 오른쪽 절반 차지) -->
          <div class="hero-search">
            <!-- ✅ 더 이상 @submit 없음 -->
            <SearchBar />
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import SearchBar from '@/components/SearchBar.vue'

export default {
  name: 'HomeView',
  components: { SearchBar },
}
</script>

<style scoped>
/* ----- Layout ----- */
.home {
  min-height: 100vh;
  background-color: #ffffff;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
    sans-serif;
}

/* ----- HERO (메인) ----- */
.hero {
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  width: 100vw;

  background-color: #2f3a45;
  min-height: 680px;
  display: flex;
  justify-content: center;
}

.hero-inner {
  width: 100%;
  max-width: 1120px;
  padding: 96px 48px 120px;
  display: flex;
  align-items: center;          /* 상하 중앙 정렬 */
  justify-content: space-between;
  gap: 80px;
}

/* 왼쪽 텍스트 영역: 항상 왼쪽 정렬 & 이동 없음 */
.hero-text {
  flex: 0 0 45%;
  max-width: 520px;
  text-align: left;
}

.hero-title {
  font-size: 40px;
  line-height: 1.2;
  color: #ffffff;
  margin-bottom: 16px;
  font-weight: 700;
}

.hero-desc {
  font-size: 15px;
  line-height: 1.6;
  color: #d9d9d9;
  margin-top: 8px;
}

/* 오른쪽 SearchBar 영역: 오른쪽 절반 차지, 수직 중앙 */
.hero-search {
  flex: 0 0 45%;
  display: flex;
  justify-content: flex-end;
  align-items: center;          /* 검색창을 수직 중앙 */
}

/* SearchBar 컴포넌트가 컬럼 안에서 꽉 차게 */
.hero-search :deep(.search-bar) {
  width: 100%;
}

@media (max-width: 768px) {
  .hero-inner {
    flex-direction: column;
    gap: 40px;
    padding: 56px 16px 72px;
  }

  .hero-text,
  .hero-search {
    flex: 1 1 auto;
    max-width: 100%;
  }
}
</style>
