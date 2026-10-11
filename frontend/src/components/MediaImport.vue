<script setup lang="ts">
import { ref } from 'vue'
import { Upload } from 'lucide-vue-next'
import type { UploadedDocument } from '../types/upload'

const fileInput = ref<HTMLInputElement>()
const selectedFileName = ref('')
const statusMessage = ref('')
const isUploading = ref(false)
const emit = defineEmits<{ 'transcription-complete': [document: UploadedDocument] }>()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// 点击按钮触发文件选择器
function openFilePicker() {
  fileInput.value?.click()
}

function handleFileChange() {
  const input = fileInput.value
  const file = input.files?.[0]
  if (!file) return

  selectedFileName.value = file.name
  void uploadFile(file)
  input.value = ''
}

async function uploadFile(file: File) {
  isUploading.value = true
  statusMessage.value = '正在上传...'

  try {
    const body = new FormData()
    body.append('file', file)
    const response = await fetch(`${apiBaseUrl}/api/uploads`, { method: 'POST', body })
    if (!response.ok) throw new Error(await response.text())

    const { task_id: taskId } = (await response.json()) as { task_id: string }
    await pollTask(taskId)
  } catch (error) {
    statusMessage.value = error instanceof Error ? error.message : '上传失败'
  } finally {
    isUploading.value = false
  }
}

async function pollTask(taskId: string) {
  for (;;) {
    await new Promise((resolve) => window.setTimeout(resolve, 1000))
    const response = await fetch(`${apiBaseUrl}/api/uploads/${taskId}`)
    if (!response.ok) throw new Error(await response.text())

    const task = (await response.json()) as {
      status: 'uploaded' | 'processing' | 'transcribing' | 'completed' | 'failed'
      filename: string | null
      text: string | null
      error: string | null
    }
    if (task.status === 'completed' && task.text) {
      emit('transcription-complete', {
        title: task.filename || '导入文档',
        summary: '由上传的媒体文件生成的转写文档。',
        content: task.text,
        audio: { label: task.filename || '导入音频', src: '' },
      })
      statusMessage.value = '转写完成'
      return
    }
    if (task.status === 'failed') throw new Error(task.error || '处理失败')
    statusMessage.value = task.status === 'processing' ? '正在提取音频...' : '正在转写...'
  }
}
</script>

<template>
  <div class="media-import">
    <input
      ref="fileInput"
      class="media-import-input"
      type="file"
      accept="audio/*,video/*"
      @change="handleFileChange"
    />
    <button type="button" class="media-import-button" :disabled="isUploading" @click="openFilePicker">
      <Upload :size="16" />
      <span>导入音频 / 视频</span>
    </button>
    <span v-if="selectedFileName" class="media-import-name" :title="selectedFileName">
      {{ selectedFileName }}
    </span>
    <span v-if="statusMessage" class="media-import-status">{{ statusMessage }}</span>
  </div>
</template>
