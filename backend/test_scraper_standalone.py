#!/usr/bin/env python3
"""
Script de test simple pour vérifier le scraper BrainyQuote
"""
import asyncio
import sys
import os

# Ajouter le chemin du backend au Python path
sys.path.insert(0, '/home/juste/Work/Web-Scrapping-Test/backend')

from src.scraper.brainyquote import BrainyQuoteScraper

async def test_scraper():
    """Test simple du scraper"""
    print("🔍 Test du scraper BrainyQuote...")

    try:
        async with BrainyQuoteScraper() as scraper:
            print("✅ Scraper initialisé")

            # Test avec le sujet motivational
            topic = "motivational"
            print(f"📝 Scraping du sujet: {topic}")

            quotes = await scraper.test_scraping(topic, limit=3)

            print(f"✅ Scraping terminé! {len(quotes)} citations trouvées:")

            for i, quote in enumerate(quotes, 1):
                print(f"\n--- Citation {i} ---")
                print(f"Texte: {quote.get('text', 'N/A')}")
                print(f"Auteur: {quote.get('author', 'N/A')}")
                print(f"Lien: {quote.get('link', 'N/A')}")
                print(f"Image: {quote.get('image_url', 'N/A')}")

            return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage du test du scraper...")

    # Vérifier que nous sommes dans le bon environnement
    if not os.path.exists('/home/juste/Work/Web-Scrapping-Test/backend/src'):
        print("❌ Erreur: Script doit être exécuté depuis le dossier backend")
        sys.exit(1)

    success = asyncio.run(test_scraper())

    if success:
        print("\n🎉 Test réussi! Le scraper fonctionne correctement.")
    else:
        print("\n💥 Test échoué! Vérifiez les logs ci-dessus.")
        sys.exit(1)