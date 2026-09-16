<script setup lang="ts">
import { computed, ref } from 'vue'
import { Pause, Play, RotateCcw, RotateCw } from 'lucide-vue-next'

const props = defineProps<{ label: string; src: string }>()

const audioElement = ref<HTMLAudioElement>()
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const hasAudio = computed(() => Boolean(props.src))

async function togglePlayback() {
  const audio = audioElement.value
  if (!audio || !hasAudio.value) return

  if (audio.paused) {
    try {
      await audio.play()
    } catch {
      isPlaying.value = false
    }
  } else {
    audio.pause()
  }
}

function updateDuration() {
  const audio = audioElement.value
  duration.value = audio && Number.isFinite(audio.duration) ? audio.duration : 0
}

function updateCurrentTime() {
  currentTime.value = audioElement.value?.currentTime ?? 0
}

function seek(event: Event) {
  const audio = audioElement.value
  if (!audio) return

  const target = event.currentTarget as HTMLInputElement
  audio.currentTime = Number(target.value)
  currentTime.value = audio.currentTime
}

function skip(seconds: number) {
  const audio = audioElement.value
  if (!audio || duration.value === 0) return

  audio.currentTime = Math.min(Math.max(audio.currentTime + seconds, 0), duration.value)
  currentTime.value = audio.currentTime
}

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds)) return '00:00'

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`
}
</script>

<template>
  <div class="audio-player" aria-label="音频播放器">
    <p class="audio-label">音频材料 · {{ label }}</p>

    <audio
      ref="audioElement"
      :src="src || undefined"
      preload="metadata"
      @loadedmetadata="updateDuration"
      @durationchange="updateDuration"
      @timeupdate="updateCurrentTime"
      @play="isPlaying = true"
      @pause="isPlaying = false"
      @ended="isPlaying = false"
    ></audio>

    <div class="audio-timeline">
      <input
        class="audio-progress"
        type="range"
        min="0"
        :max="duration || 0"
        step="0.1"
        :value="currentTime"
        :disabled="!hasAudio || duration === 0"
        aria-label="音频进度"
        @input="seek"
      />
      <div class="audio-time">
        <span>{{ formatTime(currentTime) }}</span>
        <span>{{ formatTime(duration) }}</span>
      </div>
    </div>

    <div class="audio-controls">
      <button
        type="button"
        :disabled="!hasAudio"
        aria-label="后退 10 秒"
        @click="skip(-10)"
      >
        <RotateCcw :size="17" />
        <span>10</span>
      </button>
      <button
        class="audio-play-button"
        type="button"
        :disabled="!hasAudio"
        :aria-label="isPlaying ? '暂停' : '播放'"
        @click="togglePlayback"
      >
        <Pause v-if="isPlaying" :size="18" />
        <Play v-else :size="18" />
      </button>
      <button
        type="button"
        :disabled="!hasAudio"
        aria-label="前进 10 秒"
        @click="skip(10)"
      >
        <RotateCw :size="17" />
        <span>10</span>
      </button>
    </div>

    <p v-if="!hasAudio" class="audio-placeholder">等待导入音频</p>
  </div>
</template>
