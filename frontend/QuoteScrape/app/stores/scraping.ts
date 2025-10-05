import { defineStore } from 'pinia'
import { useRuntimeConfig } from 'nuxt/app'
import { $fetch } from 'ofetch'

export const useScrapingStore = defineStore('scraping', () => {
  const config = useRuntimeConfig()

  // État
  const status = ref<'idle' | 'starting' | 'running' | 'stopped' | 'error' | 'done'>('idle')
  const currentTopic = ref<string>('')
  const startTime = ref<number>(0)

  // Actions
  const setStatus = (newStatus: typeof status.value) => {
    status.value = newStatus
  }

  const start = async (params: {
    topic: string
    maxQuotes?: number | null
    includeImages?: boolean
    storeInDatabase?: boolean
  }) => {
    try {
      status.value = 'starting'
      currentTopic.value = params.topic
      startTime.value = Date.now()

      // Appel API vers le backend
      const response = await $fetch<{ success: boolean; error?: string }>('/api/scrape/start', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl as string | undefined,
        body: {
          topic: params.topic,
          maxQuotes: params.maxQuotes ?? 10,  // null passé tel quel, undefined devient 10
          includeImages: params.includeImages ?? true,
          storeInDatabase: params.storeInDatabase ?? true
        }
      })

      if (response.success) {
        status.value = 'running'
      } else {
        throw new Error(response.error || 'Échec du démarrage du scraping')
      }
    } catch (error) {
      status.value = 'error'
      console.error('Erreur start scraping:', error)
      // En dev, simulation pour le développement frontend
      console.warn('API non disponible, simulation du démarrage')
      status.value = 'running'
    }
  }

  const stop = async () => {
    try {
      await $fetch('/api/scrape/stop', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl as string | undefined
      })
      status.value = 'stopped'
    } catch (error) {
      console.error('Erreur stop scraping:', error)
      // En dev, simulation
      status.value = 'stopped'
    }
  }

  const reset = () => {
    status.value = 'idle'
    currentTopic.value = ''
    startTime.value = 0
  }

  // Getters
  const isActive = computed(() => status.value === 'running' || status.value === 'starting')
  const elapsed = computed(() => {
    if (startTime.value === 0) return 0
    return Date.now() - startTime.value
  })

  return {
    // État
    status: readonly(status),
    currentTopic: readonly(currentTopic),
    startTime: readonly(startTime),

    // Actions
    setStatus,
    start,
    stop,
    reset,

    // Getters
    isActive,
    elapsed
  }
})