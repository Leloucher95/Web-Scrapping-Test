<template>
  <div class="quotes-list">
    <div v-if="quotes.length === 0" class="text-center py-12 text-gray-500">
      <div class="text-6xl mb-4">📝</div>
      <p class="text-lg">Aucune citation pour le moment</p>
      <p class="text-sm">Lancez un scraping pour commencer à collecter des citations</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Filtre et tri -->
      <div class="flex flex-wrap gap-4 items-center justify-between bg-gray-50 p-4 rounded-lg">
        <div class="flex items-center space-x-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Filtrer par auteur</label>
            <select v-model="filterAuthor" class="border rounded-lg px-3 py-2 text-sm">
              <option value="">Tous les auteurs</option>
              <option v-for="author in uniqueAuthors" :key="author" :value="author">
                {{ author }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Trier par</label>
            <select v-model="sortBy" class="border rounded-lg px-3 py-2 text-sm">
              <option value="newest">Plus récent</option>
              <option value="oldest">Plus ancien</option>
              <option value="author">Auteur A-Z</option>
              <option value="length">Longueur</option>
            </select>
          </div>
        </div>

        <div class="text-sm text-gray-600">
          {{ filteredQuotes.length }} citation{{ filteredQuotes.length > 1 ? 's' : '' }}
        </div>
      </div>

      <!-- Liste des citations -->
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
        <div
          v-for="quote in paginatedQuotes"
          :key="quote.id"
          class="quote-card bg-white border rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden"
        >
          <!-- Image si disponible -->
          <div v-if="quote.imageUrl" class="h-32 bg-gray-100 overflow-hidden">
            <img
              :src="quote.imageUrl"
              :alt="`Citation de ${quote.author}`"
              class="w-full h-full object-cover"
              @error="handleImageError"
            />
          </div>

          <div class="p-6">
            <!-- Texte de la citation -->
            <blockquote class="text-gray-800 text-lg leading-relaxed mb-4 italic">
              "{{ quote.text }}"
            </blockquote>

            <!-- Auteur et métadonnées -->
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-gray-900">{{ quote.author }}</p>
                <div class="flex items-center space-x-3 text-sm text-gray-500 mt-1">
                  <span v-if="quote.topic" class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    {{ quote.topic }}
                  </span>
                  <span v-if="quote.createdAt">
                    {{ formatDate(quote.createdAt) }}
                  </span>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center space-x-2">
                <button
                  @click="copyQuote(quote)"
                  class="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                  title="Copier la citation"
                >
                  📋
                </button>
                <button
                  @click="shareQuote(quote)"
                  class="p-2 text-gray-400 hover:text-green-600 transition-colors"
                  title="Partager"
                >
                  🔗
                </button>
                <button
                  @click="favoriteQuote(quote)"
                  class="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  title="Favori"
                >
                  ❤️
                </button>
              </div>
            </div>

            <!-- Statistiques de caractères -->
            <div class="mt-3 pt-3 border-t border-gray-100">
              <div class="flex justify-between text-xs text-gray-500">
                <span>{{ quote.text.length }} caractères</span>
                <span>{{ quote.text.split(' ').length }} mots</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center items-center space-x-4 mt-8">
        <button
          @click="currentPage--"
          :disabled="currentPage === 1"
          class="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          ← Précédent
        </button>

        <div class="flex space-x-2">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="currentPage = page"
            :class="[
              'px-3 py-2 rounded-lg',
              currentPage === page
                ? 'bg-blue-600 text-white'
                : 'border hover:bg-gray-50'
            ]"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="currentPage++"
          :disabled="currentPage === totalPages"
          class="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          Suivant →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Quote } from '@/stores/quotes'

interface Props {
  quotes: Quote[]
}

const props = defineProps<Props>()

// État local
const filterAuthor = ref('')
const sortBy = ref('newest')
const currentPage = ref(1)
const itemsPerPage = 6

// Auteurs uniques pour le filtre
const uniqueAuthors = computed(() => {
  const authors = props.quotes.map(quote => quote.author)
  return [...new Set(authors)].sort()
})

// Citations filtrées et triées
const filteredQuotes = computed(() => {
  let filtered = props.quotes

  // Filtrer par auteur
  if (filterAuthor.value) {
    filtered = filtered.filter(quote => quote.author === filterAuthor.value)
  }

  // Trier
  filtered = [...filtered].sort((a, b) => {
    switch (sortBy.value) {
      case 'newest':
        return new Date(b.createdAt || 0).getTime() - new Date(a.createdAt || 0).getTime()
      case 'oldest':
        return new Date(a.createdAt || 0).getTime() - new Date(b.createdAt || 0).getTime()
      case 'author':
        return a.author.localeCompare(b.author)
      case 'length':
        return b.text.length - a.text.length
      default:
        return 0
    }
  })

  return filtered
})

// Pagination
const totalPages = computed(() => Math.ceil(filteredQuotes.value.length / itemsPerPage))
const paginatedQuotes = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredQuotes.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// Méthodes
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const copyQuote = async (quote: Quote) => {
  const text = `"${quote.text}" - ${quote.author}`
  try {
    await navigator.clipboard.writeText(text)
    // Toast notification (pourrait être ajouté avec une library de notifications)
    console.log('Citation copiée !')
  } catch (error) {
    console.error('Erreur copie:', error)
  }
}

const shareQuote = (quote: Quote) => {
  const text = `"${quote.text}" - ${quote.author}`
  const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`
  window.open(url, '_blank')
}

const favoriteQuote = (quote: Quote) => {
  // Implémentation des favoris (localStorage ou API)
  console.log('Ajouté aux favoris:', quote.author)
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

// Réinitialiser la pagination quand les filtres changent
watch([filterAuthor, sortBy], () => {
  currentPage.value = 1
})
</script>

<style scoped>
.quote-card {
  transition: transform 0.2s ease-in-out;
}

.quote-card:hover {
  transform: translateY(-2px);
}

blockquote::before {
  content: '"';
  font-size: 4rem;
  color: #e5e7eb;
  position: absolute;
  left: -0.5rem;
  top: -1rem;
  font-family: serif;
}

blockquote {
  position: relative;
}
</style>