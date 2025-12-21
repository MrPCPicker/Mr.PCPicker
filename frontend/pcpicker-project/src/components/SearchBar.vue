<template>
  <div
    class="search-bar"
    :class="{ 'is-active': isExpanded }"
    @click="handleClick"
  >
    <label class="search-label">Search for...</label>

    <!-- input → textarea -->
    <textarea
      ref="searchInput"
      class="search-input"
      v-model="inputValue"
      @blur="onBlur"
      @keydown.enter="handleEnter"
      aria-label="Search for"
    ></textarea>

    <button
      v-if="buttonVisible"
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
  // ✅ 더 이상 'submit' emit 안 함
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

      this.isExpanded = true
      this.$emit('active-change', true)

      setTimeout(() => this.focusInput(), 600)
      setTimeout(() => (this.buttonVisible = true), 800)
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
        this.$emit('active-change', false)
      }
    },

    handleEnter(e) {
      // Shift + Enter => 줄바꿈
      if (e.shiftKey) return
      // 그냥 Enter => Search
      e.preventDefault()
      this.performSearch()
    },

    performSearch() {
      const query = this.inputValue.trim()
      if (!query) return

      console.log('Searching:', query)

      // ✅ 여기서만 추천 페이지로 이동
      this.$router.push({
        name: 'Recommend',
        query: { q: query }
      })
    }
  }
}
</script>

<style scoped>
/* 공통 폰트 적용 */
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

/* Expand */
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
  letter-spacing: -0.01em;
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
  letter-spacing: -0.01em;
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

.search-bar.is-active .search-input {
  margin-top: 40px;
  pointer-events: auto;
}

/* Search button */
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
  letter-spacing: 0.01em;
  cursor: pointer;

  opacity: 0;
  transform: translateY(-8px);
  animation: fadeIn 0.4s ease-out forwards;
}

.search-submit:hover {
  opacity: 0.92;
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
