# 🎨 PLAN FRONTEND NUXT.JS - Interface de Contrôle du Scraper

## 📋 **EXIGENCES FRONTEND À IMPLÉMENTER**

### 1. **Formulaire de saisie du sujet** 📝
### 2. **Bouton de lancement du scraper** ▶️
### 3. **Indicateur de progression en temps réel** 📊
### 4. **Bouton d'arrêt du scraper** ⏹️
### 5. **Export données (CSV/JSON)** 💾
### 6. **Interface responsive et conviviale** 📱

---

## 🏗️ **ARCHITECTURE TECHNIQUE**

### **Stack Frontend**
```
Nuxt.js 3 + Vue 3 + TypeScript
├── UI Framework: Tailwind CSS + Headless UI
├── State Management: Pinia
├── Communication: Socket.IO + Axios
├── Charts: Chart.js ou D3.js
└── Export: Papa Parse (CSV) + File Saver
```

### **Structure du projet**
```
frontend/QuoteScrape/
├── components/           # Composants réutilisables
│   ├── ScrapingForm.vue     # Formulaire principal
│   ├── ProgressIndicator.vue # Indicateur progression
│   ├── QuotesList.vue       # Affichage citations
│   ├── ExportButtons.vue    # Boutons export
│   └── StatsCards.vue       # Cartes statistiques
├── pages/               # Pages Nuxt
│   ├── index.vue           # Page principale
│   ├── dashboard.vue       # Tableau de bord
│   └── history.vue         # Historique jobs
├── stores/              # État global (Pinia)
│   ├── scraping.ts         # État scraping
│   ├── quotes.ts           # Citations
│   └── ui.ts               # Interface utilisateur
├── composables/         # Logique réutilisable
│   ├── useWebSocket.ts     # WebSocket client
│   ├── useExport.ts        # Export données
│   └── useNotifications.ts # Notifications
├── server/              # API Nuxt (optionnel)
│   └── api/                # Endpoints proxy
└── types/               # Types TypeScript
    ├── scraping.ts         # Types scraping
    └── api.ts              # Types API
```

---

## 🎯 **SPÉCIFICATIONS DÉTAILLÉES**

### 1. **Formulaire de saisie du sujet** 📝

#### **Composant : `ScrapingForm.vue`**
```vue
<template>
  <form @submit.prevent="startScraping" class="bg-white p-6 rounded-lg shadow-lg">
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Sujet à scraper
      </label>
      <select v-model="selectedTopic" class="form-select w-full">
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
      <input v-model.number="maxQuotes" type="number"
             min="1" max="100" value="10"
             class="form-input w-full">
    </div>

    <div class="mb-6">
      <label class="flex items-center">
        <input v-model="includeImages" type="checkbox" class="form-checkbox">
        <span class="ml-2">Télécharger les images</span>
      </label>
    </div>

    <button type="submit"
            :disabled="isScrapingActive"
            class="btn-primary w-full">
      <PlayIcon v-if="!isScrapingActive" class="w-5 h-5 mr-2" />
      <LoadingIcon v-else class="w-5 h-5 mr-2 animate-spin" />
      {{ isScrapingActive ? 'Scraping en cours...' : 'Lancer le scraping' }}
    </button>
  </form>
</template>
```

#### **Fonctionnalités**
- ✅ Dropdown sujets prédéfinis
- ✅ Champ personnalisé optionnel
- ✅ Slider nombre de citations (1-100)
- ✅ Checkbox téléchargement images
- ✅ Validation formulaire en temps réel
- ✅ Désactivation pendant scraping actif

### 2. **Bouton de lancement du scraper** ▶️

#### **Logique d'activation**
```typescript
// stores/scraping.ts
export const useScrapingStore = defineStore('scraping', {
  state: () => ({
    isActive: false,
    jobId: null as string | null,
    status: 'idle' as 'idle' | 'starting' | 'running' | 'completed' | 'error'
  }),

  actions: {
    async startScraping(params: ScrapingParams) {
      this.isActive = true
      this.status = 'starting'

      try {
        const response = await $fetch('/api/scraping/start', {
          method: 'POST',
          body: params
        })

        this.jobId = response.jobId
        this.status = 'running'

        // Démarrer le WebSocket pour suivre la progression
        await this.connectWebSocket()

      } catch (error) {
        this.status = 'error'
        throw error
      }
    }
  }
})
```

### 3. **Indicateur de progression en temps réel** 📊

#### **Composant : `ProgressIndicator.vue`**
```vue
<template>
  <div class="bg-white p-6 rounded-lg shadow-lg">
    <!-- Barre de progression principale -->
    <div class="mb-4">
      <div class="flex justify-between text-sm text-gray-600 mb-2">
        <span>Progression globale</span>
        <span>{{ progress.current }}/{{ progress.total }} citations</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-3">
        <div class="bg-blue-500 h-3 rounded-full transition-all duration-300"
             :style="{ width: `${progressPercentage}%` }"></div>
      </div>
    </div>

    <!-- Statistiques en temps réel -->
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

    <!-- Log en temps réel -->
    <div class="bg-gray-900 text-green-400 p-4 rounded-lg h-40 overflow-y-auto font-mono text-sm">
      <div v-for="log in recentLogs" :key="log.id" class="mb-1">
        [{{ formatTime(log.timestamp) }}] {{ log.message }}
      </div>
    </div>
  </div>
</template>
```

#### **WebSocket en temps réel**
```typescript
// composables/useWebSocket.ts
export const useWebSocket = () => {
  const socket = ref(null)
  const isConnected = ref(false)

  const connect = () => {
    socket.value = io('ws://localhost:8000/ws', {
      transports: ['websocket']
    })

    socket.value.on('connect', () => {
      isConnected.value = true
    })

    socket.value.on('scraping:progress', (data) => {
      const scrapingStore = useScrapingStore()
      scrapingStore.updateProgress(data)
    })

    socket.value.on('scraping:log', (data) => {
      const scrapingStore = useScrapingStore()
      scrapingStore.addLog(data)
    })

    socket.value.on('scraping:complete', (data) => {
      const scrapingStore = useScrapingStore()
      scrapingStore.completeJob(data)
    })
  }

  return { connect, isConnected }
}
```

### 4. **Bouton d'arrêt du scraper** ⏹️

#### **Composant : `StopButton.vue`**
```vue
<template>
  <button @click="stopScraping"
          :disabled="!canStop"
          class="btn-danger">
    <StopIcon class="w-5 h-5 mr-2" />
    Arrêter le scraping
  </button>

  <!-- Modal de confirmation -->
  <ConfirmModal v-model="showConfirm"
                title="Arrêter le scraping ?"
                message="Êtes-vous sûr de vouloir arrêter le scraping en cours ?"
                @confirm="confirmStop" />
</template>

<script setup>
const stopScraping = async () => {
  showConfirm.value = true
}

const confirmStop = async () => {
  try {
    await $fetch(`/api/scraping/${jobId}/stop`, { method: 'POST' })
    // Le WebSocket recevra la confirmation d'arrêt
  } catch (error) {
    console.error('Erreur arrêt scraping:', error)
  }
}
</script>
```

### 5. **Export données (CSV/JSON)** 💾

#### **Composant : `ExportButtons.vue`**
```vue
<template>
  <div class="flex space-x-4">
    <button @click="exportCSV" class="btn-secondary">
      <DownloadIcon class="w-5 h-5 mr-2" />
      Export CSV
    </button>

    <button @click="exportJSON" class="btn-secondary">
      <DownloadIcon class="w-5 h-5 mr-2" />
      Export JSON
    </button>

    <button @click="exportExcel" class="btn-secondary">
      <DownloadIcon class="w-5 h-5 mr-2" />
      Export Excel
    </button>
  </div>
</template>
```

#### **Composable d'export**
```typescript
// composables/useExport.ts
export const useExport = () => {
  const exportCSV = (quotes: Quote[]) => {
    const csv = Papa.unparse(quotes.map(q => ({
      'Auteur': q.author,
      'Citation': q.text,
      'Lien': q.source_url,
      'Catégorie': q.category,
      'Date extraction': new Date(q.extracted_at).toLocaleDateString()
    })))

    const blob = new Blob([csv], { type: 'text/csv' })
    saveAs(blob, `citations-${Date.now()}.csv`)
  }

  const exportJSON = (quotes: Quote[]) => {
    const json = JSON.stringify(quotes, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    saveAs(blob, `citations-${Date.now()}.json`)
  }

  return { exportCSV, exportJSON }
}
```

### 6. **Interface responsive et conviviale** 📱

#### **Page principale : `index.vue`**
```vue
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <h1 class="text-2xl font-bold text-gray-900">
            BrainyQuote Scraper
          </h1>
          <StatsDisplay />
        </div>
      </div>
    </header>

    <!-- Layout principal -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Colonne formulaire -->
        <div class="lg:col-span-1">
          <ScrapingForm />
          <div class="mt-6" v-if="isScrapingActive">
            <StopButton />
          </div>
        </div>

        <!-- Colonne progression -->
        <div class="lg:col-span-2">
          <ProgressIndicator v-if="isScrapingActive" />
          <QuotesDisplay v-else />
        </div>
      </div>
    </main>

    <!-- Footer actions -->
    <footer class="bg-white border-t" v-if="hasQuotes">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ExportButtons />
      </div>
    </footer>
  </div>
</template>
```

---

## 🚀 **PLAN D'IMPLÉMENTATION**

### **Phase 1 - Setup & Architecture (2-3 jours)**
1. ✅ Configuration Nuxt.js 3 + TypeScript
2. ✅ Installation dépendances (Tailwind, Pinia, Socket.IO)
3. ✅ Structure dossiers et types TypeScript
4. ✅ Configuration variables d'environnement

### **Phase 2 - Composants Core (3-4 jours)**
1. ✅ `ScrapingForm.vue` - Formulaire principal
2. ✅ `ProgressIndicator.vue` - Indicateur temps réel
3. ✅ Store Pinia pour état scraping
4. ✅ WebSocket client pour progression

### **Phase 3 - Fonctionnalités Avancées (2-3 jours)**
1. ✅ Bouton d'arrêt avec confirmation
2. ✅ Export CSV/JSON/Excel
3. ✅ Affichage citations avec pagination
4. ✅ Statistiques et graphiques

### **Phase 4 - UI/UX & Responsive (2 jours)**
1. ✅ Design responsive mobile-first
2. ✅ Animations et transitions
3. ✅ Loading states et feedback
4. ✅ Gestion erreurs avec toasts

### **Phase 5 - Tests & Deploy (1-2 jours)**
1. ✅ Tests unitaires composants
2. ✅ Tests E2E Playwright
3. ✅ Build production optimisé
4. ✅ Déploiement Vercel/Netlify

---

## 🔗 **API BACKEND REQUISE**

### **Endpoints à implémenter**
```typescript
// FastAPI endpoints nécessaires
POST /api/scraping/start    // Démarrer scraping
POST /api/scraping/{id}/stop // Arrêter scraping
GET  /api/scraping/{id}     // Status du job
GET  /api/quotes           // Liste citations
GET  /api/quotes/export    // Export données
WebSocket /ws              // Progression temps réel
```

### **Types partagés**
```typescript
interface ScrapingJob {
  id: string
  topic: string
  status: 'pending' | 'running' | 'completed' | 'stopped' | 'error'
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
}

interface Quote {
  id: string
  text: string
  author: string
  source_url: string
  supabase_image_url?: string
  category: string
  extracted_at: string
}
```

---

## 📱 **DESIGN RESPONSIVE**

### **Breakpoints Tailwind**
- `sm:` 640px+ (Mobile landscape)
- `md:` 768px+ (Tablet)
- `lg:` 1024px+ (Desktop)
- `xl:` 1280px+ (Large desktop)

### **Adaptations mobiles**
- Navigation hamburger sur mobile
- Formulaire en pleine largeur
- Stack vertical des composants
- Touch-friendly boutons et inputs
- Swipe gestures pour navigation

---

## 🎨 **IDENTITÉ VISUELLE**

### **Palette de couleurs**
```css
:root {
  --primary: #3B82F6;    /* Blue-500 */
  --success: #10B981;    /* Emerald-500 */
  --warning: #F59E0B;    /* Amber-500 */
  --error: #EF4444;      /* Red-500 */
  --gray-50: #F9FAFB;
  --gray-900: #111827;
}
```

### **Composants UI**
- Cards avec ombres subtiles
- Boutons avec états hover/focus
- Inputs avec validation visuelle
- Toasts notifications élégantes
- Modals avec backdrop blur

---

## ✅ **CHECKLIST FINALE**

### **Fonctionnalités obligatoires**
- [ ] Formulaire saisie sujet ✅
- [ ] Bouton lancement scraper ✅
- [ ] Indicateur progression temps réel ✅
- [ ] Bouton arrêt scraper ✅
- [ ] Export CSV/JSON ✅
- [ ] Interface responsive ✅

### **Fonctionnalités bonus**
- [ ] Historique jobs de scraping
- [ ] Filtres et recherche citations
- [ ] Graphiques statistiques interactifs
- [ ] Mode sombre/clair
- [ ] Notifications push
- [ ] Cache offline PWA

**Le frontend sera une interface moderne, intuitive et performante pour contrôler parfaitement le scraper BrainyQuote !** 🚀