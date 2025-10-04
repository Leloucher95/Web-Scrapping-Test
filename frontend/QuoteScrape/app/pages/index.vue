<template>
  <section>
    <h2 class="text-2xl font-bold mb-2">BrainyQuote Scraper</h2>
    <p class="text-gray-600 mb-6">Extrayez des citations avec images et stockage automatique en base de données.</p>

    <div class="grid gap-6 lg:grid-cols-3">
      <!-- Formulaire de configuration -->
      <div class="lg:col-span-1">
        <div class="p-6 rounded-lg border bg-white shadow-lg">
          <h3 class="font-semibold mb-4">Configuration du scraping</h3>
          <form @submit.prevent="startScraping" class="space-y-4">
            <!-- Sélection du sujet -->
            <div>
              <label class="block text-sm font-medium mb-2" for="topic">Sujet</label>
              <select id="topic" v-model="formData.topic"
                      class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      :disabled="isScrapingActive">
                <option value="motivational">Motivationnel</option>
                <option value="love">Amour</option>
                <option value="success">Succès</option>
                <option value="wisdom">Sagesse</option>
                <option value="life">Vie</option>
                <option value="happiness">Bonheur</option>
              </select>
            </div>

            <!-- Nombre max de citations -->
            <div>
              <label class="block text-sm font-medium mb-2" for="maxQuotes">
                Nombre max de citations ({{ formData.maxQuotes }})
              </label>
              <input id="maxQuotes" v-model.number="formData.maxQuotes"
                     type="range" min="1" max="50"
                     class="w-full"
                     :disabled="isScrapingActive" />
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>1</span>
                <span>50</span>
              </div>
            </div>

            <!-- Options -->
            <div class="space-y-3">
              <label class="flex items-center">
                <input v-model="formData.includeImages"
                       type="checkbox"
                       class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                       :disabled="isScrapingActive" />
                <span class="ml-2 text-sm">Télécharger les images</span>
              </label>

              <label class="flex items-center">
                <input v-model="formData.storeInDatabase"
                       type="checkbox"
                       class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                       :disabled="isScrapingActive" />
                <span class="ml-2 text-sm">Stocker en base de données</span>
              </label>
            </div>

            <!-- Boutons d'action -->
            <div class="space-y-3">
              <button type="submit"
                      :disabled="isScrapingActive"
                      class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center">
                <span v-if="!isScrapingActive" class="mr-2">▶️</span>
                <span v-else class="mr-2">⏳</span>
                {{ isScrapingActive ? 'Scraping en cours...' : 'Lancer le scraping' }}
              </button>

              <button v-if="isScrapingActive && canStop"
                      @click="stopScraping"
                      type="button"
                      class="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center">
                <span class="mr-2">⏹️</span>
                Arrêter le scraping
              </button>
            </div>
          </form>
        </div>

        <!-- Export des données -->
        <div v-if="quotes.items.length > 0" class="mt-6 p-6 rounded-lg border bg-white shadow-lg">
          <h3 class="font-semibold mb-4">Export des données</h3>
          <div class="grid grid-cols-2 gap-3">
            <button @click="exportCSV"
                    class="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-lg text-sm flex items-center justify-center">
              📄 CSV
            </button>
            <button @click="exportJSON"
                    class="bg-purple-600 hover:bg-purple-700 text-white py-2 px-3 rounded-lg text-sm flex items-center justify-center">
              📋 JSON
            </button>
          </div>
        </div>
      </div>

      <!-- Zone principale de contenu -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Indicateur de progression -->
        <div v-if="isScrapingActive" class="p-6 rounded-lg border bg-white shadow-lg">
          <h3 class="font-semibold mb-4">Progression du scraping</h3>

          <!-- Barre de progression -->
          <div class="mb-6">
            <div class="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progression</span>
              <span>{{ progress.current }}/{{ progress.total }} citations</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
              <div class="bg-blue-500 h-3 rounded-full transition-all duration-300"
                   :style="{ width: `${progressPercentage}%` }"></div>
            </div>
            <div class="text-center text-lg font-semibold mt-2">
              {{ progressPercentage }}%
            </div>
          </div>

          <!-- Statistiques -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ stats.extracted }}</div>
              <div class="text-sm text-gray-500">Extraites</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ stats.images }}</div>
              <div class="text-sm text-gray-500">Images</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-yellow-600">{{ stats.errors }}</div>
              <div class="text-sm text-gray-500">Erreurs</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ formatTime(stats.elapsed) }}</div>
              <div class="text-sm text-gray-500">Temps</div>
            </div>
          </div>

          <!-- Logs de progression -->
          <div>
            <h4 class="font-medium mb-2">Logs en temps réel</h4>
            <div class="bg-gray-900 text-green-400 p-4 rounded-lg h-32 overflow-y-auto font-mono text-sm">
              <div v-for="log in recentLogs" :key="log.id" class="mb-1">
                [{{ formatTime(log.timestamp) }}] {{ log.message }}
              </div>
              <div v-if="recentLogs.length === 0" class="text-gray-500">
                En attente de logs...
              </div>
            </div>
          </div>
        </div>

        <!-- Statut simple quand pas de scraping -->
        <div v-else class="p-6 rounded-lg border bg-white shadow-lg">
          <h3 class="font-semibold mb-2">Statut</h3>
          <ScrapingStatus :status="status" />
          <p class="text-gray-600 mt-2">
            Configurez les paramètres et lancez un scraping pour commencer.
          </p>
        </div>

        <!-- Liste des citations -->
        <div class="p-6 rounded-lg border bg-white shadow-lg">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-semibold">Citations extraites ({{ quotes.items.length }})</h3>
            <div v-if="quotes.items.length > 0" class="text-sm text-gray-500">
              Dernière mise à jour: {{ formatTime(Date.now()) }}
            </div>
          </div>
          <QuotesList :quotes="quotes.items" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface FormData {
  topic: string
  maxQuotes: number
  includeImages: boolean
  storeInDatabase: boolean
}

interface Progress {
  current: number
  total: number
}

interface Stats {
  extracted: number
  images: number
  errors: number
  elapsed: number
}

interface Log {
  id: number
  timestamp: number
  message: string
}

const scrapingStore = useScrapingStore()
const quotes = useQuotesStore()

// État local
const formData = ref<FormData>({
  topic: 'motivational',
  maxQuotes: 10,
  includeImages: true,
  storeInDatabase: true
})

const progress = ref<Progress>({
  current: 0,
  total: 0
})

const stats = ref<Stats>({
  extracted: 0,
  images: 0,
  errors: 0,
  elapsed: 0
})

const recentLogs = ref<Log[]>([])
const logCounter = ref(0)

// États calculés
const isScrapingActive = computed(() => scrapingStore.status === 'running')
const canStop = computed(() => isScrapingActive.value && progress.value.current > 0)
const progressPercentage = computed(() => {
  if (progress.value.total === 0) return 0
  return Math.round((progress.value.current / progress.value.total) * 100)
})
const status = computed(() => scrapingStore.status)

// WebSocket pour les mises à jour temps réel
let websocket: WebSocket | null = null

// Méthodes
const startScraping = async () => {
  try {
    resetStats()
    scrapingStore.setStatus('starting')

    // Ajouter log
    addLog('Démarrage du scraping...')

    // Connecter WebSocket si pas déjà fait
    if (!websocket) {
      connectWebSocket()
    }

    // Appel via le store
    await scrapingStore.start({
      topic: formData.value.topic,
      maxQuotes: formData.value.maxQuotes,
      includeImages: formData.value.includeImages,
      storeInDatabase: formData.value.storeInDatabase
    })

    progress.value.total = formData.value.maxQuotes
    addLog(`Scraping démarré pour "${formData.value.topic}"`)
  } catch (error) {
    console.error('Erreur démarrage scraping:', error)
    scrapingStore.setStatus('error')
    addLog(`Erreur: ${error}`)
  }
}

const stopScraping = async () => {
  if (!confirm('Êtes-vous sûr de vouloir arrêter le scraping en cours ?')) {
    return
  }

  try {
    await scrapingStore.stop()
    addLog('Scraping arrêté par l\'utilisateur')
  } catch (error) {
    console.error('Erreur arrêt scraping:', error)
    addLog(`Erreur lors de l'arrêt: ${error}`)
  }
}

const exportCSV = () => {
  const headers = ['ID', 'Auteur', 'Citation', 'Sujet']
  const csvContent = [
    headers.join(','),
    ...quotes.items.map(quote => [
      quote.id,
      `"${quote.author}"`,
      `"${quote.text.replace(/"/g, '""')}"`,
      quote.topic || ''
    ].join(','))
  ].join('\n')

  downloadFile(csvContent, 'quotes.csv', 'text/csv')
  addLog(`Export CSV: ${quotes.items.length} citations`)
}

const exportJSON = () => {
  const jsonContent = JSON.stringify(quotes.items, null, 2)
  downloadFile(jsonContent, 'quotes.json', 'application/json')
  addLog(`Export JSON: ${quotes.items.length} citations`)
}

const downloadFile = (content: string, filename: string, contentType: string) => {
  const blob = new Blob([content], { type: contentType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const resetStats = () => {
  progress.value = { current: 0, total: 0 }
  stats.value = { extracted: 0, images: 0, errors: 0, elapsed: 0 }
  recentLogs.value = []
  logCounter.value = 0
}

const addLog = (message: string) => {
  const newLog: Log = {
    id: ++logCounter.value,
    timestamp: Date.now(),
    message
  }

  recentLogs.value.push(newLog)

  // Garder seulement les 20 derniers logs
  if (recentLogs.value.length > 20) {
    recentLogs.value = recentLogs.value.slice(-20)
  }
}

const connectWebSocket = () => {
  const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${wsProtocol}//${location.host}/ws/scraping`

  websocket = new WebSocket(wsUrl)

  websocket.onopen = () => {
    addLog('Connexion WebSocket établie')
  }

  websocket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    } catch (error) {
      console.error('Erreur parsing WebSocket:', error)
    }
  }

  websocket.onclose = () => {
    addLog('Connexion WebSocket fermée')
    websocket = null
  }

  websocket.onerror = (error) => {
    console.error('Erreur WebSocket:', error)
    addLog('Erreur de connexion WebSocket')
  }
}

const handleWebSocketMessage = (data: any) => {
  switch (data.type) {
    case 'progress':
      progress.value.current = data.current
      progress.value.total = data.total
      break

    case 'quote_extracted':
      stats.value.extracted++
      quotes.addQuote(data.quote)
      addLog(`Citation extraite: ${data.quote.author}`)
      break

    case 'image_downloaded':
      stats.value.images++
      addLog(`Image téléchargée: ${data.filename}`)
      break

    case 'error':
      stats.value.errors++
      addLog(`Erreur: ${data.message}`)
      break

    case 'completed':
      scrapingStore.setStatus('done')
      addLog('Scraping terminé avec succès')
      break

    case 'status':
      scrapingStore.setStatus(data.status)
      break

    default:
      addLog(data.message || 'Message WebSocket reçu')
  }

  // Mettre à jour le temps écoulé
  if (data.elapsed) {
    stats.value.elapsed = data.elapsed
  }
}

// Nettoyage à la destruction du composant
onUnmounted(() => {
  if (websocket) {
    websocket.close()
  }
})

// Charger les exemples de citations au montage
onMounted(() => {
  quotes.loadSample()
  addLog('Interface initialisée')
})
</script>
