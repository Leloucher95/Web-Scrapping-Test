<template>
  <section>
    <h2 class="text-2xl font-bold mb-2">Bienvenue</h2>
    <p class="text-gray-600 mb-6">Frontend Nuxt est prêt. La connexion API et WebSocket sera branchée ensuite.</p>

    <div class="grid gap-4 sm:grid-cols-2">
      <div class="p-4 rounded-lg border bg-white">
        <h3 class="font-semibold mb-2">Démarrer un scraping</h3>
        <form @submit.prevent="startScraping">
          <label class="block text-sm mb-1" for="topic">Sujet</label>
          <input id="topic" v-model="topic" class="w-full border rounded px-3 py-2 mb-3" placeholder="ex: love" />
          <button type="submit" class="px-3 py-2 bg-black text-white rounded hover:bg-gray-800 disabled:opacity-50" :disabled="loading">
            {{ loading ? 'En cours…' : 'Lancer' }}
          </button>
        </form>
      </div>

      <div class="p-4 rounded-lg border bg-white">
        <h3 class="font-semibold mb-2">Statut</h3>
        <ScrapingStatus :status="status" />
      </div>
    </div>

    <div class="mt-6 p-4 rounded-lg border bg-white">
      <h3 class="font-semibold mb-2">Citations</h3>
      <QuotesList :quotes="quotes.items" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useScrapingStore } from '@/stores/scraping'
import { useQuotesStore } from '@/stores/quotes'

const topic = ref('love')
const status = ref<'idle' | 'starting' | 'running' | 'error' | 'done'>('idle')
const loading = ref(false)

const scraping = useScrapingStore()
const quotes = useQuotesStore()

onMounted(() => {
  quotes.loadSample(topic.value)
})

async function startScraping() {
  loading.value = true
  status.value = 'starting'
  try {
    await scraping.start(topic.value)
    status.value = 'running'
  } catch (e) {
    console.error(e)
    status.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>
