export default defineEventHandler(async (event) => {
  try {
    // Configuration de l'API backend
    const backendUrl = 'http://localhost:8000' // URL du backend FastAPI

    // Appel vers le backend Python pour arrêter le scraping
    const response = await $fetch(`${backendUrl}/api/scrape/stop`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    return {
      success: true,
      data: response,
      message: 'Scraping arrêté avec succès'
    }
  } catch (error) {
    console.error('Erreur API stop scraping:', error)

    // En développement, simulation de succès
    if (process.env.NODE_ENV === 'development') {
      return {
        success: true,
        data: { status: 'stopped' },
        message: 'Mode développement - arrêt simulé'
      }
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Erreur lors de l\'arrêt du scraping',
      data: error
    })
  }
})