<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { Link2, Loader2, X } from 'lucide-vue-next'
import type { UploadedDocument } from '../types/upload'

// 后端 /api/parse 返回的字幕结构（与上传接口不同：text 是数组，不是字符串）
type SubtitleSegment = { start: number; end: number; text: string }

type ParseTask = {
  status: 'uploaded' | 'processing' | 'completed' | 'failed'
  text: SubtitleSegment[] | null
  title?: string
  error: string | null
}

const emit = defineEmits<{ 'transcription-complete': [document: UploadedDocument] }>()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const STATUS_TEXT: Record<ParseTask['status'], string> = {
  uploaded: '已提交，等待解析...',
  processing: '正在解析视频字幕...',
  completed: '解析完成',
  failed: '解析失败',
}

const isOpen = ref(false)
const videoUrl = ref('')
const isParsing = ref(false)
const statusMessage = ref('')
const errorMessage = ref('')
const inputElement = ref<HTMLInputElement>()

const POLL_INTERVAL = 1000
const POLL_MAX_ATTEMPTS = 120

let abortController: AbortController | null = null
let isUnmounted = false

// 打开弹窗时清空状态，聚焦输入框
function openModal() {
  videoUrl.value = ''
  statusMessage.value = ''
  errorMessage.value = ''
  isParsing.value = false
  isOpen.value = true
  void nextTick(() => inputElement.value?.focus())
}

function closeModal() {
  isOpen.value = false
}

// 解析中不允许关窗，避免轮询结果丢失
function requestClose() {
  if (isParsing.value) return
  closeModal()
}
// esc关闭
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && isOpen.value) requestClose()
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
// 销毁前终止与外部的各种请求，避免内存泄漏
onBeforeUnmount(() => {
  isUnmounted = true
  abortController?.abort()
  window.removeEventListener('keydown', handleKeydown)
})

// 后端出错时返回的是 {"detail": "..."}，比直接读 text() 干净
async function readError(response: Response, fallback: string) {
  try {
    const data = (await response.json()) as { detail?: string }
    return data.detail || fallback
  } catch {
    return fallback
  }
}

function isAbortError(error: unknown) {
  return error instanceof Error && error.name === 'AbortError'
}

async function submitUrl() {
  const url = videoUrl.value.trim()
  if (!url) {
    errorMessage.value = '请先粘贴 B 站视频链接或 BV 号'
    return
  }

  isParsing.value = true
  errorMessage.value = ''
  statusMessage.value = '正在提交解析任务...'
  // 如果上一次解析还没结束，先取消它
  abortController?.abort()
  abortController = new AbortController()
  const { signal } = abortController

  try {
    // 提交解析任务，获取 task_id
    const response = await fetch(`${apiBaseUrl}/api/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
      signal,
    })
    if (!response.ok) {
      throw new Error(await readError(response, `提交失败（HTTP ${response.status}）`))
    }

    const { task_id: taskId } = (await response.json()) as { task_id?: string }
    if (!taskId) throw new Error('提交失败：未获取到任务 ID')
    // 轮询查询解析结果
    await pollParseTask(taskId, signal)
  } catch (error) {
    if (isAbortError(error)) return
    errorMessage.value = error instanceof Error ? error.message : '解析失败'
    isParsing.value = false
  }
}

async function pollParseTask(taskId: string, signal: AbortSignal) {
  for (let attempt = 0; attempt < POLL_MAX_ATTEMPTS; attempt++) {
    // 后端没有实现长连接，只能定时轮询
    await new Promise((resolve) => window.setTimeout(resolve, POLL_INTERVAL))
    if (isUnmounted || signal.aborted) return

    const response = await fetch(`${apiBaseUrl}/api/parse/${taskId}`, { signal })
    if (!response.ok) {
      throw new Error(await readError(response, `查询任务失败（HTTP ${response.status}）`))
    }

    // 拿到解析结果，更新提示信息
    const task = (await response.json()) as ParseTask
    statusMessage.value = STATUS_TEXT[task.status] ?? task.status

    if (task.status === 'completed') {
      if (!task.text?.length) throw new Error('解析完成，但没有取到字幕内容')

      const title = task.title || '未命名视频'
      closeModal()
      emit('transcription-complete', {
        title,
        summary: `来自 B 站视频的字幕，共 ${task.text.length} 条。`,
        content: task.text.map((item) => item.text).join('\n'),
        // 目前 player.vue 只认 <audio> 的 src，B站 iframe 还没接，先留空
        audio: { label: title, src: '' },
      })
      return
    }

    if (task.status === 'failed') {
      throw new Error(task.error || '解析失败')
    }
  }

  throw new Error('解析超时，请稍后重试')
}
</script>

<template>
  <div class="video-import">
    <button type="button" class="media-import-button" @click="openModal">
      <Link2 :size="16" />
      <span>粘贴视频链接</span>
    </button>
  </div>

  <Teleport to="body">
    <div v-if="isOpen" class="modal-mask" @click.self="requestClose">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="video-import-title">
        <div class="modal-heading">
          <h3 id="video-import-title">粘贴 B 站视频链接</h3>
          <button
            type="button"
            class="modal-close"
            aria-label="关闭"
            :disabled="isParsing"
            @click="requestClose"
          >
            <X :size="16" />
          </button>
        </div>

        <p class="modal-hint">支持完整链接（含 bilibili.com/video/BV…），也可以直接粘贴 BV 号。</p>

        <input
          ref="inputElement"
          v-model="videoUrl"
          class="modal-input"
          type="text"
          placeholder="https://www.bilibili.com/video/BV1xx411c7mD"
          :disabled="isParsing"
          @keyup.enter="submitUrl"
        />

        <p v-if="statusMessage && !errorMessage" class="modal-status">{{ statusMessage }}</p>
        <p v-if="errorMessage" class="modal-error">{{ errorMessage }}</p>

        <div class="modal-actions">
          <button type="button" class="modal-button ghost" :disabled="isParsing" @click="requestClose">
            取消
          </button>
          <button type="button" class="modal-button primary" :disabled="isParsing" @click="submitUrl">
            <Loader2 v-if="isParsing" :size="15" class="modal-spin" />
            <span>{{ isParsing ? '解析中...' : '开始解析' }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
