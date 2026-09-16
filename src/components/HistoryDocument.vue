<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { BookOpen, Clock3, FileText } from 'lucide-vue-next'
import { useDocumentStore } from '../stores/document'

const documentStore = useDocumentStore()
const { documents, selectedDocumentId } = storeToRefs(documentStore)
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
