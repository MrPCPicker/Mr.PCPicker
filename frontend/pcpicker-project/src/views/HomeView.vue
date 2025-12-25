<template>
  <div class="home">
    <main>
      <section class="hero">
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
              <span class="dot"></span> Expert Selection
            </div>
            <h1 class="hero-title">
              Build the <span class="highlight-blue">Perfect PC</span><br />
              for your needs
            </h1>
            <p class="hero-desc">
              로고의 회로처럼 정교한 분석 시스템을 통해<br />
              <strong>Mr.PC Picker</strong>가 최적의 부품 조합을 제안합니다.
            </p>
            
            <div class="hero-features">
              <div class="feature-item">
                <strong>2,000+</strong>
                <span>Database</span>
              </div>
              <div class="divider"></div>
              <div class="feature-item">
                <strong>Real-time</strong>
                <span>Price Track</span>
              </div>
            </div>
          </div>

          <div class="hero-search animate-fade-left">
            <div class="search-premium-card">
              <div class="card-header">
                <h3>Start Your Search</h3>
                <p>무엇을 찾고 계신가요?</p>
              </div>
              <div class="search-bar-wrapper">
                <SearchBar />
              </div>
            </div>
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
  components: { 
    SearchBar 
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

.home {
  min-height: 100vh;
  background-color: #ffffff;
  font-family: 'Inter', 'Pretendard', sans-serif;
}

/* ----- 히어로 섹션: 배경색 수정 (가장자리 가시성 확보) ----- */
.hero {
  position: relative;
  width: 100%;
  min-height: 750px;
  /* 가장자리를 기존보다 밝게 조정하여 회로가 묻히지 않게 함 */
  background: radial-gradient(circle at 50% 50%, #25334a 0%, #1e293b 45%, #1a2436 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

/* ----- 회로 애니메이션 배경 스타일 ----- */
.circuit-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.5; /* 가시성 상향 */
  z-index: 0;
}

.circuit-line {
  stroke: #60a5fa; /* 더 선명하고 밝은 파란색으로 변경 */
  stroke-width: 1.2;
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: drawLine 2.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.circuit-node {
  fill: #60a5fa;
  opacity: 0;
  animation: fadeInNode 0.5s ease forwards;
  animation-delay: 2s;
}

@keyframes drawLine {
  to { stroke-dashoffset: 0; }
}

@keyframes fadeInNode {
  to { opacity: 1; }
}

/* ----- 배경 효과 보강 ----- */
.bg-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
  opacity: 0.05;
  z-index: 1;
}

.bg-glow {
  position: absolute;
  width: 1000px; /* 글로우를 키워 전체 조도 향상 */
  height: 1000px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.18;
  z-index: 1;
}

.blob-main {
  background: #3B82F6;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.hero-inner {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 1100px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 50px;
}

/* ----- 콘텐츠 애니메이션 (기존 유지) ----- */
.animate-fade-up {
  opacity: 0;
  transform: translateY(30px);
  animation: contentFadeUp 1s ease forwards;
  animation-delay: 0.5s;
}

.animate-fade-left {
  opacity: 0;
  transform: translateX(30px);
  animation: contentFadeLeft 1s ease forwards;
  animation-delay: 0.8s;
}

@keyframes contentFadeUp {
  to { opacity: 1; transform: translateY(0); }
}

@keyframes contentFadeLeft {
  to { opacity: 1; transform: translateX(0); }
}

/* ----- 텍스트 영역 (기존 유지) ----- */
.hero-text {
  flex: 1;
  max-width: 500px;
  color: #ffffff;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  color: #60a5fa;
  margin-bottom: 24px;
}

.hero-badge .dot {
  width: 6px;
  height: 6px;
  background-color: #3B82F6;
  border-radius: 50%;
  box-shadow: 0 0 8px #3B82F6;
}

.hero-title {
  font-size: 52px;
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.03em;
  margin-bottom: 20px;
}

.highlight-blue {
  color: #3B82F6;
}

.hero-desc {
  font-size: 17px;
  line-height: 1.6;
  color: #94a3b8;
  margin-bottom: 40px;
}

/* ----- 기능 지표 (기존 유지) ----- */
.hero-features {
  display: flex;
  gap: 30px;
}

.feature-item strong {
  font-size: 20px;
  color: #ffffff;
  display: block;
}

.feature-item span {
  font-size: 13px;
  color: #64748b;
}

.divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
}

/* ----- 검색창 카드 (기존 구조 및 스타일 유지) ----- */
.hero-search {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.search-premium-card {
  width: 100%;
  max-width: 440px;
  background: #ffffff;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 
              0 0 20px rgba(59, 130, 246, 0.2);
}

.card-header h3 {
  font-size: 22px;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 6px;
}

.card-header p {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 30px;
}

.search-bar-wrapper {
  background: #f8fafc;
  border-radius: 12px;
  padding: 4px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
}

.search-bar-wrapper:focus-within {
  border-color: #3B82F6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.card-footer {
  margin-top: 20px;
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
}

.hero-search :deep(.search-bar) {
  width: 100%;
}

@media (max-width: 768px) {
  .hero-inner {
    flex-direction: column;
    text-align: center;
    padding: 80px 24px;
  }
  .hero-text { margin-bottom: 50px; }
  .hero-features { justify-content: center; }
  .hero-search { width: 100%; justify-content: center; }
}
</style>