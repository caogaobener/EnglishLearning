<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { BookMarked } from 'lucide-vue-next'
import { useDocumentStore } from '../stores/document'

const documentStore = useDocumentStore()
const { selectedDocument } = storeToRefs(documentStore)
</script>

<template>
  <aside class="notebook-float" aria-label="单词本">
    <div class="notebook-heading">
      <div class="panel-title">
        <BookMarked :size="18" />
        <strong>当前生词</strong>
      </div>
    </div>
    <template v-if="selectedDocument">
      <p class="notebook-hint">已记录 {{ selectedDocument.vocabulary.length }} 个单词</p>
      <ul v-if="selectedDocument.vocabulary.length">
        <li v-for="word in selectedDocument.vocabulary" :key="word">{{ word }}</li>
      </ul>
      <p v-else class="notebook-hint">这篇文档暂时没有生词</p>
    </template>
    <p v-else class="notebook-hint">请选择一篇文档</p>
  </aside>
</template>
