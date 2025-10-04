export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { topic, maxQuotes = 10, includeImages = true, storeInDatabase = true } = body

    // Configuration de l'API backend
    const backendUrl = 'http://localhost:8000' // URL du backend FastAPI

    // Appel vers le backend Python
    const response = await $fetch(`${backendUrl}/api/scrape/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        topic,
        max_quotes: maxQuotes,
        include_images: includeImages,
        store_in_database: storeInDatabase
      }
    })

    return {
      success: true,
      data: response,
      message: `Scraping démarré pour "${topic}"`
    }
  } catch (error) {
    console.error('Erreur API start scraping:', error)

    // En développement, simulation de succès pour tester le frontend
    if (process.env.NODE_ENV === 'development') {
      return {
        success: true,
        data: { status: 'started' },
        message: 'Mode développement - scraping simulé'
      }
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Erreur lors du démarrage du scraping',
      data: error
    })
  }
})