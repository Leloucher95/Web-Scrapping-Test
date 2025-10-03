import { defineStore } from 'pinia'
import { useRuntimeConfig } from 'nuxt/app'
import { $fetch } from 'ofetch'

export const useScrapingStore = defineStore('scraping', () => {
  const config = useRuntimeConfig()

  async function start(topic: string) {
    // Appel API placeholder - sera relié au backend FastAPI
    await $fetch('/api/scrape/start', {
      method: 'POST',
      baseURL: config.public.apiBaseUrl as string | undefined,
      body: { topic }
    }).catch((err: unknown) => {
      // En dev, pas d'API encore disponible
      console.warn('API non disponible, simulation du démarrage', err)
    })
  }

  return { start }
})