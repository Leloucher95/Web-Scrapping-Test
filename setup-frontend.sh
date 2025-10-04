#!/bin/bash

# 🚀 Script de setup et démarrage du frontend Nuxt.js
# BrainyQuote Scraper Interface

echo "🎨 Setting up BrainyQuote Scraper Frontend..."

# Variables
FRONTEND_DIR="frontend/QuoteScrape"
BACKEND_URL="http://localhost:8000"

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "💡 Please install Node.js from: https://nodejs.org/"
    exit 1
fi

# Vérifier si pnpm est installé (recommandé pour Nuxt 3)
if ! command -v pnpm &> /dev/null; then
    echo "📦 Installing pnpm globally..."
    npm install -g pnpm
fi

# Créer le projet Nuxt.js s'il n'existe pas
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "🏗️  Creating Nuxt.js project..."
    cd frontend/
    pnpx nuxi@latest init QuoteScrape
    cd QuoteScrape/
else
    echo "📁 Frontend project already exists"
    cd "$FRONTEND_DIR"
fi

# Installer les dépendances
echo "📦 Installing dependencies..."
pnpm install

# Ajouter les dépendances requises
echo "🔧 Adding required packages..."
pnpm add -D @nuxt/tailwindcss @nuxtjs/color-mode @pinia/nuxt @vueuse/nuxt
pnpm add pinia socket.io-client papaparse file-saver chart.js vue-chartjs
pnpm add @headlessui/vue @heroicons/vue axios

# Créer la structure de dossiers
echo "📂 Creating project structure..."
mkdir -p components/scraping
mkdir -p components/ui
mkdir -p stores
mkdir -p composables
mkdir -p types
mkdir -p server/api/scraping

# Créer le fichier de configuration Nuxt
cat > nuxt.config.ts << 'EOF'
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/color-mode',
    '@pinia/nuxt',
    '@vueuse/nuxt'
  ],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
      wsUrl: process.env.WS_URL || 'ws://localhost:8000'
    }
  },
  colorMode: {
    classSuffix: ''
  },
  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: 'tailwind.config.js'
  }
})
EOF

# Créer le fichier CSS principal
mkdir -p assets/css
cat > assets/css/main.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center;
  }

  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center;
  }

  .btn-danger {
    @apply bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center;
  }

  .form-input {
    @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500;
  }

  .form-select {
    @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500;
  }

  .form-checkbox {
    @apply h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded;
  }

  .card {
    @apply bg-white rounded-lg shadow-lg p-6;
  }
}
EOF

# Créer les types TypeScript
cat > types/scraping.ts << 'EOF'
export interface ScrapingJob {
  id: string
  topic: string
  status: 'pending' | 'starting' | 'running' | 'completed' | 'stopped' | 'error'
  progress: {
    current: number
    total: number
    percentage: number
  }
  stats: {
    extracted: number
    images: number
    errors: number
    elapsed: number
  }
  startedAt: string
  completedAt?: string
  errorMessage?: string
}

export interface Quote {
  id: string
  text: string
  author: string
  source_url: string
  supabase_image_url?: string
  category: string
  extracted_at: string
}

export interface ScrapingParams {
  topic: string
  maxQuotes: number
  includeImages: boolean
}

export interface LogEntry {
  id: string
  timestamp: number
  level: 'info' | 'warning' | 'error'
  message: string
}
EOF

# Créer le store Pinia principal
cat > stores/scraping.ts << 'EOF'
import { defineStore } from 'pinia'
import type { ScrapingJob, ScrapingParams, LogEntry } from '~/types/scraping'

export const useScrapingStore = defineStore('scraping', {
  state: () => ({
    currentJob: null as ScrapingJob | null,
    isActive: false,
    logs: [] as LogEntry[],
    jobHistory: [] as ScrapingJob[]
  }),

  getters: {
    progressPercentage: (state) => {
      if (!state.currentJob?.progress.total) return 0
      return Math.round((state.currentJob.progress.current / state.currentJob.progress.total) * 100)
    },

    canStop: (state) => {
      return state.isActive && state.currentJob?.status === 'running'
    }
  },

  actions: {
    async startScraping(params: ScrapingParams) {
      try {
        this.isActive = true

        const { data } = await $fetch<{ jobId: string }>('/api/scraping/start', {
          method: 'POST',
          body: params
        })

        this.currentJob = {
          id: data.jobId,
          topic: params.topic,
          status: 'starting',
          progress: { current: 0, total: params.maxQuotes, percentage: 0 },
          stats: { extracted: 0, images: 0, errors: 0, elapsed: 0 },
          startedAt: new Date().toISOString()
        }

      } catch (error) {
        this.isActive = false
        throw error
      }
    },

    async stopScraping() {
      if (!this.currentJob) return

      await $fetch(`/api/scraping/${this.currentJob.id}/stop`, {
        method: 'POST'
      })
    },

    updateProgress(data: Partial<ScrapingJob>) {
      if (this.currentJob) {
        Object.assign(this.currentJob, data)
      }
    },

    addLog(log: Omit<LogEntry, 'id'>) {
      this.logs.unshift({
        ...log,
        id: Date.now().toString()
      })

      // Garder seulement les 100 derniers logs
      if (this.logs.length > 100) {
        this.logs = this.logs.slice(0, 100)
      }
    },

    completeJob(data: Partial<ScrapingJob>) {
      if (this.currentJob) {
        Object.assign(this.currentJob, data)
        this.jobHistory.unshift({ ...this.currentJob })
        this.isActive = false
      }
    }
  }
})
EOF

# Créer la page principale
cat > pages/index.vue << 'EOF'
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <h1 class="text-2xl font-bold text-gray-900">
            🧠 BrainyQuote Scraper
          </h1>
          <div class="text-sm text-gray-500">
            Interface de contrôle du scraper
          </div>
        </div>
      </div>
    </header>

    <!-- Layout principal -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Colonne formulaire -->
        <div class="lg:col-span-1 space-y-6">
          <ScrapingForm />

          <div v-if="scrapingStore.canStop" class="card">
            <button @click="stopScraping" class="btn-danger w-full">
              ⏹️ Arrêter le scraping
            </button>
          </div>
        </div>

        <!-- Colonne contenu principal -->
        <div class="lg:col-span-2">
          <ProgressIndicator v-if="scrapingStore.isActive" />
          <div v-else class="card">
            <h2 class="text-xl font-semibold mb-4">Prêt à commencer</h2>
            <p class="text-gray-600">
              Sélectionnez un sujet et lancez le scraping pour extraire des citations de BrainyQuote.
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
const scrapingStore = useScrapingStore()

const stopScraping = async () => {
  try {
    await scrapingStore.stopScraping()
  } catch (error) {
    console.error('Erreur lors de l\'arrêt:', error)
  }
}
</script>
EOF

# Créer un composant de formulaire basique
cat > components/ScrapingForm.vue << 'EOF'
<template>
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Configuration du scraping</h2>

    <form @submit.prevent="startScraping">
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Sujet
        </label>
        <select v-model="form.topic" class="form-select">
          <option value="motivational">Motivationnel</option>
          <option value="love">Amour</option>
          <option value="success">Succès</option>
          <option value="wisdom">Sagesse</option>
          <option value="life">Vie</option>
          <option value="happiness">Bonheur</option>
        </select>
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Nombre max de citations
        </label>
        <input v-model.number="form.maxQuotes"
               type="number" min="1" max="100"
               class="form-input">
      </div>

      <div class="mb-6">
        <label class="flex items-center">
          <input v-model="form.includeImages"
                 type="checkbox"
                 class="form-checkbox">
          <span class="ml-2 text-sm text-gray-700">Télécharger les images</span>
        </label>
      </div>

      <button type="submit"
              :disabled="scrapingStore.isActive"
              class="btn-primary w-full">
        {{ scrapingStore.isActive ? '⏳ Scraping en cours...' : '▶️ Lancer le scraping' }}
      </button>
    </form>
  </div>
</template>

<script setup>
const scrapingStore = useScrapingStore()

const form = reactive({
  topic: 'motivational',
  maxQuotes: 10,
  includeImages: true
})

const startScraping = async () => {
  try {
    await scrapingStore.startScraping(form)
  } catch (error) {
    console.error('Erreur lors du démarrage:', error)
  }
}
</script>
EOF

# Créer un composant d'indicateur de progression basique
cat > components/ProgressIndicator.vue << 'EOF'
<template>
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Progression du scraping</h2>

    <!-- Barre de progression -->
    <div class="mb-6">
      <div class="flex justify-between text-sm text-gray-600 mb-2">
        <span>Progression</span>
        <span>{{ scrapingStore.currentJob?.progress.current || 0 }}/{{ scrapingStore.currentJob?.progress.total || 0 }}</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-3">
        <div class="bg-blue-500 h-3 rounded-full transition-all duration-300"
             :style="{ width: `${scrapingStore.progressPercentage}%` }"></div>
      </div>
      <div class="text-center text-lg font-semibold mt-2">
        {{ scrapingStore.progressPercentage }}%
      </div>
    </div>

    <!-- Statistiques -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="text-center">
        <div class="text-2xl font-bold text-green-600">
          {{ scrapingStore.currentJob?.stats.extracted || 0 }}
        </div>
        <div class="text-sm text-gray-500">Extraites</div>
      </div>
      <div class="text-center">
        <div class="text-2xl font-bold text-blue-600">
          {{ scrapingStore.currentJob?.stats.images || 0 }}
        </div>
        <div class="text-sm text-gray-500">Images</div>
      </div>
      <div class="text-center">
        <div class="text-2xl font-bold text-yellow-600">
          {{ scrapingStore.currentJob?.stats.errors || 0 }}
        </div>
        <div class="text-sm text-gray-500">Erreurs</div>
      </div>
      <div class="text-center">
        <div class="text-2xl font-bold text-purple-600">
          {{ formatTime(scrapingStore.currentJob?.stats.elapsed || 0) }}
        </div>
        <div class="text-sm text-gray-500">Temps</div>
      </div>
    </div>
  </div>
</template>

<script setup>
const scrapingStore = useScrapingStore()

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>
EOF

# Créer un fichier .env exemple
cat > .env.example << 'EOF'
# API Backend URL
API_BASE_URL=http://localhost:8000

# WebSocket URL
WS_URL=ws://localhost:8000

# Supabase (pour accès direct si nécessaire)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
EOF

echo "✅ Frontend setup completed!"
echo ""
echo "🚀 Next steps:"
echo "1. cd $FRONTEND_DIR"
echo "2. Copy .env.example to .env and configure URLs"
echo "3. pnpm dev (to start development server)"
echo ""
echo "📚 The frontend will be available at: http://localhost:3000"
echo "🔗 Make sure the backend is running at: $BACKEND_URL"
echo ""
echo "🎨 Happy coding!"