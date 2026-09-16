<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { FileText, MoreHorizontal, Search } from 'lucide-vue-next'
import { useDocumentStore } from '../stores/document'
import Player from './player.vue'

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
    <article v-if="selectedDocument" class="document-content">
      <p class="document-kicker">{{ selectedDocument.kicker }}</p>
      <h1>{{ selectedDocument.title }}</h1>
      <p>{{ selectedDocument.summary }}</p>
      <Player
        :key="selectedDocument.id"
        :label="selectedDocument.audio.label"
        :src="selectedDocument.audio.src"
      />
      <div class="document-divider"></div>
      <p class="document-copy">{{ selectedDocument.content }}</p>
      <div v-if="selectedDocument.vocabulary.length" class="vocabulary-row">
        <span
          v-for="word in selectedDocument.vocabulary"
          :key="word"
          class="vocabulary-chip"
        >
          {{ word }}
        </span>
      </div>
      <p v-else class="document-placeholder">这篇文档暂时没有生词</p>
    </article>
    <p v-else class="panel-empty">请选择一篇文档</p>
  </section>
</template>
