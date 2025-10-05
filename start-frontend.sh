#!/bin/bash

# Script de démarrage du frontend Nuxt.js amélioré
# Ce script installe les dépendances, configure l'environnement et démarre le serveur

set -e

echo "🚀 Démarrage du frontend QuoteScrape"
echo "====================================="

# Aller dans le répertoire du frontend
cd "$(dirname "$0")/frontend/QuoteScrape"

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé. Veuillez l'installer d'abord."
    echo "   Installation recommandée: https://nodejs.org/"
    exit 1
fi

# Vérifier la version de Node.js
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_VERSION="18.0.0"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo "✅ Node.js version: $NODE_VERSION"
else
    echo "⚠️  Node.js version $NODE_VERSION détectée. Version recommandée: >=18"
fi

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    if command -v pnpm &> /dev/null; then
        pnpm install
    elif command -v yarn &> /dev/null; then
        yarn install
    else
        npm install
    fi
else
    echo "✅ Dépendances déjà installées"
fi

# Créer le fichier .env.local s'il n'existe pas
if [ ! -f ".env.local" ]; then
    echo "⚙️  Création du fichier de configuration .env.local"
    cat > .env.local << EOF
# Configuration du frontend QuoteScrape
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
NUXT_PUBLIC_WS_URL=ws://localhost:8000
NUXT_ENV=development

# Configuration optionnelle
NUXT_PORT=3000
NUXT_HOST=localhost
EOF
    echo "✅ Fichier .env.local créé"
fi

# Vérifier que le backend est accessible (optionnel)
echo "🔍 Vérification de la connexion au backend..."
if curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
    echo "✅ Backend accessible sur http://localhost:8000"
else
    echo "⚠️  Backend non accessible. Le frontend fonctionnera en mode simulation."
    echo "   Pour démarrer le backend: cd backend/src && uvicorn main:app --reload"
fi

echo ""
echo "🎯 Démarrage du serveur de développement..."
echo "   Frontend URL: http://localhost:3000"
echo "   Ctrl+C pour arrêter"
echo ""

# Démarrer le serveur de développement
if command -v pnpm &> /dev/null; then
    pnpm dev
elif command -v yarn &> /dev/null; then
    yarn dev
else
    npm run dev
fi