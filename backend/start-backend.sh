#!/bin/bash

# Script de démarrage du backend
# Utilisation: ./start-backend.sh

set -e

echo "🚀 Démarrage du backend QuoteScrape"
echo "===================================="

# Aller dans le répertoire backend
cd "$(dirname "$0")"

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv_new" ]; then
    echo "❌ Environnement virtuel non trouvé"
    echo "   Créez-le avec: python3 -m venv venv_new"
    exit 1
fi

# Activer l'environnement virtuel
echo "✅ Activation de l'environnement virtuel..."
source venv_new/bin/activate

# Vérifier que les dépendances sont installées
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Dépendances manquantes. Installation..."
    pip install -r requirements.txt
fi

# Vérifier le fichier .env
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo "   Créez-le avec vos clés Supabase"
fi

# Aller dans le dossier src
cd src

echo ""
echo "🎯 Démarrage du serveur FastAPI..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   WebSocket: ws://localhost:8000/ws/scraping"
echo ""
echo "   Ctrl+C pour arrêter"
echo ""

# Démarrer le serveur
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
