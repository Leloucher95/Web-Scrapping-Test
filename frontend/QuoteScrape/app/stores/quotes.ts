import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Quote {
  id: string
  text: string
  author: string
  topic?: string
  imageUrl?: string
  createdAt?: string
}

export const useQuotesStore = defineStore('quotes', () => {
  const items = ref<Quote[]>([])

  function loadSample(topic = 'love') {
    items.value = [
      {
        id: '1',
        text: 'Love all, trust a few, do wrong to none.',
        author: 'William Shakespeare',
        topic,
        createdAt: new Date().toISOString()
      },
      {
        id: '2',
        text: 'The best thing to hold onto in life is each other.',
        author: 'Audrey Hepburn',
        topic,
        createdAt: new Date().toISOString()
      }
    ]
  }

  function addQuote(quote: Quote) {
    // Éviter les doublons
    const exists = items.value.find(item => item.id === quote.id)
    if (!exists) {
      items.value.push({
        ...quote,
        createdAt: quote.createdAt || new Date().toISOString()
      })
    }
  }

  function removeQuote(id: string) {
    const index = items.value.findIndex(item => item.id === id)
    if (index > -1) {
      items.value.splice(index, 1)
    }
  }

  function clearQuotes() {
    items.value = []
  }

  function updateQuote(id: string, updates: Partial<Omit<Quote, 'id'>>) {
    const index = items.value.findIndex(item => item.id === id)
    if (index > -1) {
      const currentQuote = items.value[index]
      if (currentQuote) {
        items.value[index] = {
          id: currentQuote.id,
          text: updates.text ?? currentQuote.text,
          author: updates.author ?? currentQuote.author,
          topic: updates.topic ?? currentQuote.topic,
          imageUrl: updates.imageUrl ?? currentQuote.imageUrl,
          createdAt: updates.createdAt ?? currentQuote.createdAt
        }
      }
    }
  }

  // Getters
  const quotesCount = computed(() => items.value.length)
  const quotesByTopic = computed(() => {
    const grouped: Record<string, Quote[]> = {}
    items.value.forEach(quote => {
      const topic = quote.topic || 'other'
      if (!grouped[topic]) {
        grouped[topic] = []
      }
      grouped[topic].push(quote)
    })
    return grouped
  })

  return {
    items,
    loadSample,
    addQuote,
    removeQuote,
    clearQuotes,
    updateQuote,
    quotesCount,
    quotesByTopic
  }
})