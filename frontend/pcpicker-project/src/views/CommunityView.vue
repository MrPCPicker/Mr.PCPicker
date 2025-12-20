<template>
  <div class="home">
    <!-- Community Main Layout -->
    <div class="content">

      <!-- =========================
           Left List Section
      ========================== -->
      <section class="list">
        <div class="list-item" v-for="item in items" :key="item.id">
          <div class="list-avatar"></div>

          <div>
            <p class="list-title">{{ item.price }}</p>
            <ul class="list-desc">
              <li v-for="(text, index) in item.desc" :key="index">
                {{ text }}
              </li>
            </ul>
          </div>
        </div>
      </section>

      <!-- =========================
           Right Detail Section
      ========================== -->
      <section class="detail">
        <div class="detail-card">
          <p class="detail-desc">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit,
            sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
          </p>
        </div>

        <div class="detail-card">
          <h3 class="detail-title">Needs</h3>
          <ul class="detail-desc">
            <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
            <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
            <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
            <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
          </ul>
        </div>

        <div class="detail-card">
          <h3 class="detail-title">Recommend</h3>
          <ul class="detail-desc">
            <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
            <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
            <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
            <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
          </ul>
        </div>

        <div style="text-align: right;">
          <button class="header-login">Rewrite</button>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>

const items = [
  {
    id: 1,
    price: '$400,000',
    desc: [
      'Lorem ipsum dolor sit amet',
      'Lorem ipsum dolor sit amet',
      'Lorem ipsum dolor sit amet',
      'Lorem ipsum dolor sit amet',
    ],
  },
  {
    id: 2,
    price: '$400,000',
    desc: [
      'Lorem ipsum dolor sit amet',
      'Lorem ipsum dolor sit amet',
      'Lorem ipsum dolor sit amet',
      'Lorem ipsum dolor sit amet',
    ],
  },
  {
    id: 3,
    price: '$400,000',
    desc: [
      'Lorem ipsum dolor sit amet',
      'Lorem ipsum dolor sit amet',
      'Lorem ipsum dolor sit amet',
      'Lorem ipsum dolor sit amet',
    ],
  },
]
</script>

<style scoped>
/* 기존 main.css 최대 활용 → 최소 보정만 */
.list-desc {
  padding-left: 16px;
}

.list-desc li {
  list-style: disc;
}

.detail-desc li {
  margin-bottom: 6px;
}
</style>
