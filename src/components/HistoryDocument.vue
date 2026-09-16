<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { BookOpen, Clock3, FileText, Upload } from 'lucide-vue-next'
import { useDocumentStore } from '../stores/document'

const documentStore = useDocumentStore()
const { documents, selectedDocumentId } = storeToRefs(documentStore)

const mediaInput = ref<HTMLInputElement>()
const selectedMediaName = ref('')
const selectedMediaType = ref<'audio' | 'video' | ''>('')

function openMediaPicker() {
  mediaInput.value?.click()
}

function handleMediaSelect(event: Event) {
  const target = event.currentTarget as HTMLInputElement
  const file = target.files?.[0]

  if (!file) {
    selectedMediaName.value = ''
    selectedMediaType.value = ''
    return
  }

  selectedMediaName.value = file.name
  selectedMediaType.value = file.type.startsWith('video/') ? 'video' : 'audio'
}
</script>

<template>
  <aside class="workspace-panel history-panel" aria-label="历史文档">
    <div class="panel-heading">
      <div class="panel-title">
        <BookOpen :size="18" />
        <h2>历史文档</h2>
      </div>
      <span class="panel-count">{{ documents.length }}</span>
    </div>
    <div class="media-import-card">
      <p class="media-import-title">导入练习素材</p>
      <button type="button" class="media-import-button" @click="openMediaPicker">
        <Upload :size="15" />
        <span>选择音频或视频</span>
      </button>
      <input
        ref="mediaInput"
        class="media-import-input"
        type="file"
        accept="audio/*,video/*"
        @change="handleMediaSelect"
      />
      <p class="media-import-hint">
        {{ selectedMediaName ? `已选择${selectedMediaType}：${selectedMediaName}` : '支持常见音频/视频格式' }}
      </p>
    </div>
    <button
      v-for="document in documents"
      :key="document.id"
      class="document-item"
      :class="{ 'is-active': document.id === selectedDocumentId }"
      type="button"
      @click="documentStore.selectDocument(document.id)"
    >
      <FileText :size="16" />
      <span>{{ document.title }}</span>
    </button>
    <div v-if="documents.length === 0" class="panel-empty">
      <Clock3 :size="15" />
      暂无历史文档
    </div>
  </aside>
</template>
