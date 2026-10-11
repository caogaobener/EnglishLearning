<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { Bot, Send } from 'lucide-vue-next'
import { useDocumentStore } from '../stores/document'

const documentStore = useDocumentStore()
const { selectedDocument } = storeToRefs(documentStore)
</script>

<template>
  <aside class="workspace-panel chat-panel" aria-label="聊天助手">
    <div class="panel-heading">
      <div class="panel-title">
        <Bot :size="18" />
        <h2>Chat Assistant</h2>
      </div>
      <span class="status-dot" aria-label="在线"></span>
    </div>
    <template v-if="selectedDocument">
      <div class="chat-context">当前文本：{{ selectedDocument.title }}</div>
      <div class="chat-messages">
        <p
          v-for="message in selectedDocument.chatMessages"
          :key="message.id"
          class="assistant-message"
          :class="{ 'user-message': message.role === 'user' }"
        >
          {{ message.text }}
        </p>
        <p v-if="selectedDocument.chatMessages.length === 0" class="panel-empty">
          暂无聊天记录
        </p>
      </div>
    </template>
    <p v-else class="panel-empty">请选择一篇文档</p>
    <div class="chat-input">
      <input type="text" placeholder="输入你的问题..." aria-label="输入问题" disabled />
      <button type="button" aria-label="发送" disabled>
        <Send :size="16" />
      </button>
    </div>
  </aside>
</template>
