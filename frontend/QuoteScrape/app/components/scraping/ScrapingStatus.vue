<template>
  <div class="text-sm">
    <span class="inline-flex items-center gap-2">
      <span :class="badgeClass" class="w-2 h-2 rounded-full inline-block"></span>
      <span class="capitalize">{{ status }}</span>
    </span>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ status: 'idle' | 'starting' | 'running' | 'error' | 'done' }>()

const badgeClass = computed(() => {
  switch (props.status) {
    case 'idle':
      return 'bg-gray-400'
    case 'starting':
      return 'bg-amber-500'
    case 'running':
      return 'bg-blue-500 animate-pulse'
    case 'done':
      return 'bg-green-600'
    case 'error':
      return 'bg-red-600'
  }
})
</script>
