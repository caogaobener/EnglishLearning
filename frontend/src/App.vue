<script setup lang="ts">
import { ref } from 'vue'
import ChatAsistant from './components/ChatAsistant.vue'
import DocumentViewer from './components/DocumentViewer.vue'
import HistoryDocument from './components/HistoryDocument.vue'
import NoteBook from './components/NoteBook.vue'
import type { UploadedDocument } from './types/upload'

const uploadedDocument = ref<UploadedDocument>()
</script>

<template>
  <main class="workspace">
    <HistoryDocument @transcription-complete="uploadedDocument = $event" />
    <DocumentViewer :uploaded-document="uploadedDocument" />
    <ChatAsistant />
    <NoteBook />
  </main>
</template>
