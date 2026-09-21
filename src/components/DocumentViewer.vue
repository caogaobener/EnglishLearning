<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { FileText, MoreHorizontal, Search } from 'lucide-vue-next'
import { useDocumentStore } from '../stores/document'
import Player from './player.vue'
import type { UploadedDocument } from '../types/upload'

const props = defineProps<{ uploadedDocument?: UploadedDocument }>()
const documentStore = useDocumentStore()
const { selectedDocument } = storeToRefs(documentStore)
</script>

<template>
  <section class="workspace-panel document-panel" aria-label="文档查看器">
    <div class="panel-heading">
      <div class="panel-title">
        <FileText :size="18" />
        <h2>文档查看器</h2>
      </div>
      <div class="panel-actions">
        <span aria-label="搜索"><Search :size="17" /></span>
        <span aria-label="更多"><MoreHorizontal :size="18" /></span>
      </div>    
    </div>
    <Player
      v-if="selectedDocument || props.uploadedDocument"
      :key="props.uploadedDocument?.title || selectedDocument?.id"
      :label="props.uploadedDocument?.audio.label || selectedDocument?.audio.label || ''"
      :src="props.uploadedDocument?.audio.src || selectedDocument?.audio.src || ''"
    />
    <article v-if="props.uploadedDocument || selectedDocument" class="document-content">
      <p class="document-kicker">{{ props.uploadedDocument ? 'IMPORTED MEDIA' : selectedDocument?.kicker }}</p>
      <h1>{{ props.uploadedDocument?.title || selectedDocument?.title }}</h1>
      <p>{{ props.uploadedDocument?.summary || selectedDocument?.summary }}</p>
      <div class="document-divider"></div>
      <p class="document-copy">{{ props.uploadedDocument?.content || selectedDocument?.content }}</p>
      <div v-if="!props.uploadedDocument && selectedDocument?.vocabulary.length" class="vocabulary-row">
        <span
          v-for="word in selectedDocument?.vocabulary"
          :key="word"
          class="vocabulary-chip"
        >
          {{ word }}
        </span>
      </div>
      <p v-else-if="!props.uploadedDocument" class="document-placeholder">这篇文档暂时没有生词</p>
    </article>
    <p v-else class="panel-empty">请选择一篇文档</p>
  </section>
</template>
