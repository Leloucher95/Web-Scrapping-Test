import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Quote {
  id: string
  text: string
  author: string
  topic?: string
}

export const useQuotesStore = defineStore('quotes', () => {
  const items = ref<Quote[]>([])

  function loadSample(topic = 'love') {
    items.value = [
      { id: '1', text: 'Love all, trust a few, do wrong to none.', author: 'William Shakespeare', topic },
      { id: '2', text: 'The best thing to hold onto in life is each other.', author: 'Audrey Hepburn', topic }
    ]
  }

  return { items, loadSample }
})