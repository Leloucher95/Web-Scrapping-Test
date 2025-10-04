export default defineEventHandler(async (event) => {
  try {
    // Configuration de l'API backend
    const backendUrl = 'http://localhost:8000' // URL du backend FastAPI

    // Récupérer le statut depuis le backend
    const response = await $fetch(`${backendUrl}/api/scrape/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    return {
      success: true,
      data: response
    }
  } catch (error) {
    console.error('Erreur API status scraping:', error)

    // En développement, retourner un statut par défaut
    if (process.env.NODE_ENV === 'development') {
      return {
        success: true,
        data: {
          status: 'idle',
          progress: { current: 0, total: 0 },
          stats: { extracted: 0, images: 0, errors: 0, elapsed: 0 }
        }
      }
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Erreur lors de la récupération du statut',
      data: error
    })
  }
})