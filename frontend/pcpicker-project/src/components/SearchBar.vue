<template>
  <div
    class="search-bar"
    :class="{ 'is-active': isExpanded }"
    @click="handleClick"
  >
    <label class="search-label">Search for...</label>

    <input
      ref="searchInput"
      type="text"
      class="search-input"
      v-model="inputValue"
      @blur="onBlur"
      aria-label="Search for"
    />

    <!-- 버튼 페이드인 -->
    <button
      v-if="buttonVisible"
      type="button"
      class="search-submit"
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
      inputValue: ''
    }
  },
  methods: {
    handleClick() {

      if (this.isExpanded) {
        this.focusInput()
        return
      }

      // 1) 바 확장
      this.isExpanded = true
      this.$emit('active-change', true)

      // 2) 바 확대 후 커서 깜빡
      setTimeout(() => {
        this.focusInput()
      }, 600) // height transition 에 맞춤

      // 3) 버튼 페이드인
      setTimeout(() => {
        this.buttonVisible = true
      }, 800) // 커서보다 약간 늦게
    },

    focusInput() {
      if (this.isInputFocused) return
      const el = this.$refs.searchInput
      if (el) {
        el.focus()
        this.isInputFocused = true
      }
    },

    onBlur() {
      this.isInputFocused = false

      if (!this.inputValue) {
        this.isExpanded = false
        this.buttonVisible = false
        this.$emit('active-change', false)
      }
    }
  }
}
</script>

<style scoped>
/* 기본 pill */
.search-bar {
  position: relative;
  width: 100%;
  height: 56px;
  background: #f4f6fa;
  border-radius: 28px;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  cursor: text;
  transition:
    height 0.6s ease-in-out,
    padding 0.6s ease-in-out,
    box-shadow 0.6s ease-in-out;
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.18);
  overflow: hidden;
}

/* 확장 */
.search-bar.is-active {
  height: 380px;
  align-items: flex-start;
  padding-top: 22px;
}

/* 라벨 */
.search-label {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  color: #9ca3af;
  pointer-events: none;
  transition: all 0.3s ease-in-out;
}

/* 라벨 이동 */
.search-bar.is-active .search-label {
  top: 18px;
  transform: translateY(0);
  font-size: 13px;
  color: #6b21a8;
}

/* input */
.search-input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  width: 100%;
  padding: 0;
  pointer-events: none;
}

.search-bar.is-active .search-input {
  margin-top: 40px;
  pointer-events: auto;
}

/* Search 버튼 */
/* 초기 숨김 상태일 때 애니메이션 준비 (v-if로 렌더링되므로 첫 상태 필요 없음) */
.search-submit {
  position: absolute;
  right: 24px;
  bottom: 24px;
  padding: 10px 22px;
  border-radius: 999px;
  border: none;
  background: #4f46e5;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;

  /* 페이드인 + 슬라이드 효과 */
  opacity: 0;
  transform: translateY(-8px);
  animation: fadeIn 0.4s ease-out forwards;
}

/* hover */
.search-submit:hover {
  opacity: 0.85;
}

/* 페이드인 키프레임 */
@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
