<script setup>
import { ref } from 'vue'

const completedLessons = ref(3)
const totalLessons = 12
const showMessage = ref(false)

function startLesson() {
  showMessage.value = true
  window.setTimeout(() => {
    showMessage.value = false
  }, 2400)
}
</script>

<template>
  <main class="page-shell">
    <section class="hero-card">
      <div class="hero-copy">
        <p class="eyebrow">ENGLISH LEARNING</p>
        <h1>每天进步一点点，<br /><span>让英语成为你的超能力。</span></h1>
        <p class="intro">通过短小、有效的练习，建立自信，享受每一次开口表达。</p>
        <button class="primary-button" type="button" @click="startLesson">开始今日学习 <span>→</span></button>
        <p v-if="showMessage" class="success-message">太棒了！今日课程马上开始 ✨</p>
      </div>
      <div class="hero-art" aria-hidden="true">
        <div class="sun"></div>
        <div class="book book-back"></div>
        <div class="book book-front"><span>ABC</span></div>
        <div class="sparkle sparkle-one">✦</div>
        <div class="sparkle sparkle-two">✦</div>
      </div>
    </section>

    <section class="progress-card">
      <div>
        <p class="section-label">学习进度</p>
        <h2>继续保持，你已经完成 <strong>{{ completedLessons }}</strong> / {{ totalLessons }} 节课程</h2>
      </div>
      <div class="progress-track" role="progressbar" :aria-valuenow="completedLessons" :aria-valuemax="totalLessons">
        <div class="progress-fill" :style="{ width: `${(completedLessons / totalLessons) * 100}%` }"></div>
      </div>
    </section>
  </main>
</template>
