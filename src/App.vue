<script setup lang="ts">
import ChatAsistant from './components/ChatAsistant.vue'
import DocumentViewer from './components/DocumentViewer.vue'
import HistoryDocument from './components/HistoryDocument.vue'
import NoteBook from './components/NoteBook.vue'
</script>

<template>
  <main class="workspace">
    <HistoryDocument />
    <DocumentViewer />
    <ChatAsistant />
    <NoteBook />
  </main>
</template>
