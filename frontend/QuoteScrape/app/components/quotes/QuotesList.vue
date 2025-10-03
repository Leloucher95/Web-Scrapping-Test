<template>
  <div>
    <ul class="divide-y">
      <li v-for="q in quotes" :key="q.id" class="py-3">
        <blockquote class="text-gray-900">“{{ q.text }}”</blockquote>
        <div class="text-sm text-gray-600">— {{ q.author }}</div>
        <div v-if="q.topic" class="text-xs text-gray-400 mt-1">#{{ q.topic }}</div>
      </li>
    </ul>
    <div v-if="!quotes.length" class="text-sm text-gray-500">Aucune citation pour l’instant.</div>
  </div>
</template>

<script setup lang="ts">
export interface Quote {
  id: string
  text: string
  author: string
  topic?: string
}

const props = defineProps<{ quotes: Quote[] }>()
</script>
