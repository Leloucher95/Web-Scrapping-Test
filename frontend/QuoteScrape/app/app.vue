<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="border-b bg-white">
      <div class="max-w-5xl mx-auto flex items-center justify-between p-4">
        <h1 class="text-xl font-semibold">BrainyQuote Scraper</h1>
        <nav class="text-sm text-gray-600">
          <NuxtLink to="/" class="hover:text-gray-900">Accueil</NuxtLink>
        </nav>
      </div>
    </header>
    <main class="max-w-5xl mx-auto p-4">
      <NuxtRouteAnnouncer />
      <NuxtLayout>
        <NuxtPage />
      </NuxtLayout>
    </main>
  </div>

</template>
