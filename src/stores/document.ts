import { defineStore } from 'pinia'

export type ChatMessage = {
  id: number
  role: 'assistant' | 'user'
  text: string
}

export type DocumentRecord = {
  id: string
  title: string
  kicker: string
  summary: string
  content: string
  audio: {
    label: string
    src: string
  }
  vocabulary: string[]
  chatMessages: ChatMessage[]
}

const documents: DocumentRecord[] = [
  {
    id: 'notes',
    title: 'My English Notes',
    kicker: 'ENGLISH NOTES · 2026',
    summary: '整理你的日常英语表达，随时复习重点句型和常用词汇。',
    content:
      'Small, consistent practice is more effective than occasional intensive study. Read a little, notice one useful phrase, and use it in your own sentence.',
    audio: { label: 'Daily practice sample', src: '' },
    vocabulary: ['consistent', 'occasional', 'intensive'],
    chatMessages: [
      {
        id: 1,
        role: 'assistant',
        text: '这是 My English Notes 的聊天记录。我们可以讨论如何保持稳定的学习习惯。',
      },
      { id: 2, role: 'user', text: 'consistent 在这里应该怎么理解？' },
    ],
  },
  {
    id: 'travel',
    title: 'Travel Conversation',
    kicker: 'TRAVEL ENGLISH · 2026',
    summary: '练习在机场、酒店和城市出行时自然地表达自己的需求。',
    content:
      'Could you tell me how to get to the city centre? I have a reservation under the name Chen, and I would like to check in.',
    audio: { label: 'Travel conversation sample', src: '' },
    vocabulary: ['reservation', 'under the name', 'check in'],
    chatMessages: [
      {
        id: 1,
        role: 'assistant',
        text: '这是 Travel Conversation 的聊天记录。你可以练习机场和酒店场景中的表达。',
      },
      { id: 2, role: 'user', text: 'check in 可以用在哪些场景？' },
    ],
  },
  {
    id: 'daily',
    title: 'Daily Practice',
    kicker: 'DAILY PRACTICE · 2026',
    summary: '用短篇文本记录每天的输入与输出，建立稳定的学习节奏。',
    content:
      'Today I listened to an English podcast during my walk. I understood the main idea and wrote down two expressions to review later.',
    audio: { label: 'Podcast practice sample', src: '' },
    vocabulary: ['podcast', 'main idea', 'expression'],
    chatMessages: [
      {
        id: 1,
        role: 'assistant',
        text: '这是 Daily Practice 的聊天记录。你可以把今天遇到的句子记录下来。',
      },
    ],
  },
]

export const useDocumentStore = defineStore('document', {
  state: () => ({
    documents,
    selectedDocumentId: documents[0]?.id ?? '',
  }),
  getters: {
    // 根据 selectedDocumentId 获取当前选中的文档
    selectedDocument: (state): DocumentRecord | undefined =>
      state.documents.find((document) => document.id === state.selectedDocumentId),
  },
  actions: {
    selectDocument(documentId: string) {
      // 判断文档是否存在之后再更新状态
      const documentExists = this.documents.some((document) => document.id === documentId)

      if (!documentExists) return false

      this.selectedDocumentId = documentId
      return true
    },
  },
})
