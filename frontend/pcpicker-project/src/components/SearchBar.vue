<template>
  <div
    class="search-bar"
    :class="{ 'is-active': isExpanded }"
    @click="handleClick"
  >
    <label class="search-label">Search for...</label>

    <textarea
      ref="searchInput"
      class="search-input"
      v-model="inputValue"
      :placeholder="activePlaceholder"
      @blur="onBlur"
      @keydown.enter="handleEnter"
      aria-label="Search for"
    ></textarea>

    <button
      v-if="buttonVisible && isContentVisible"
      type="button"
      class="search-submit"
      @click="performSearch"
    >
      Search
    </button>
  </div>
</template>

<script>
export default {
  name: 'SearchBar',
  emits: ['active-change'],
  data() {
    return {
      isExpanded: false,
      isInputFocused: false,
      buttonVisible: false,
      isContentVisible: false, // 애니메이션 종료 후 컨텐츠 노출 제어
      inputValue: ''
    }
  },
  computed: {
    // 확장 및 컨텐츠 노출 준비가 완료되었을 때만 문구 반환
    activePlaceholder() {
      if (this.isExpanded && this.isContentVisible) {
        return '용도, 예산, 휴대성, 크기, 사용 기간, 사용 프로그램 등을 작성해주세요\n예) 대학생, 200만원 이하, UnrealEngine, 4~5년, 13인치, 노트북'
      }
      return ''
    }
  },
  methods: {
    handleClick() {
      if (this.isExpanded) {
        this.focusInput()
        return
      }

      this.isExpanded = true
      this.$emit('active-change', true)

      // 1. 애니메이션이 거의 끝날 때쯤(600ms) 커서 깜빡임 시작
      setTimeout(() => {
        this.focusInput()
      }, 600)

      // 2. 애니메이션이 완전히 종료된 후(800ms) Placeholder와 버튼 등장
      setTimeout(() => {
        this.isContentVisible = true
        this.buttonVisible = true
      }, 800)
    },

    focusInput() {
      const el = this.$refs.searchInput
      if (el) el.focus()
      this.isInputFocused = true
    },

    onBlur() {
      this.isInputFocused = false

      if (!this.inputValue.trim()) {
        this.isExpanded = false
        this.buttonVisible = false
        this.isContentVisible = false // 상태 초기화
        this.$emit('active-change', false)
      }
    },

    handleEnter(e) {
      if (e.shiftKey) return
      e.preventDefault()
      this.performSearch()
    },

    performSearch() {
      const query = this.inputValue.trim()
      if (!query) return

      this.$router.push({
        name: 'Recommend',
        query: { q: query, ts: Date.now() }
      })
    }
  }
}
</script>

<style scoped>
:host,
.search-input,
.search-label,
.search-submit {
  font-family: 'Inter', 'DM Sans', 'Pretendard', sans-serif;
}

/* ---- PILL ---- */
.search-bar {
  position: relative;
  width: 100%;
  height: 56px;
  background: #f5f7fb;
  border-radius: 28px;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  cursor: text;
  overflow: hidden;
  transition:
    height 0.6s ease-in-out,
    padding 0.6s ease-in-out,
    box-shadow 0.6s ease-in-out;
  box-shadow: 0 14px 36px rgba(0, 0, 0, 0.15);
}

.search-bar.is-active {
  height: 380px;
  align-items: flex-start;
  padding-top: 22px;
}

/* Label */
.search-label {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  font-weight: 500;
  color: #a5acb8;
  pointer-events: none;
  transition: all 0.3s ease-in-out;
}

.search-bar.is-active .search-label {
  top: 18px;
  transform: translateY(0);
  font-size: 13px;
  color: #7446e1;
}

/* Input (textarea) */
.search-input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 15.5px;
  font-weight: 500;
  line-height: 1.55;
  width: 100%;
  height: 100%;
  resize: none;
  overflow-y: auto;
  white-space: pre-wrap;
  padding: 0;
  color: #1e2125;
  pointer-events: none;
}

/* Placeholder 스타일: 나타날 때 자연스럽게 보이도록 */
.search-input::placeholder {
  color: #c1c7d0;
  font-size: 14px;
  line-height: 1.6;
  font-weight: 400;
}

.search-bar.is-active .search-input {
  margin-top: 40px;
  pointer-events: auto;
}

/* Search button (Fade-in 적용) */
.search-submit {
  position: absolute;
  right: 24px;
  bottom: 24px;
  padding: 10px 26px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #4f46e5, #6f5ce7);
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  
  /* 애니메이션 효과 */
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>