Voici le fichier Markdown complet et détaillé pour ton projet de web scraping BrainyQuote :

```markdown
# 📚 BrainyQuote Web Scraper - Documentation Complète

## 🎯 Vue d'ensemble du projet

Application de web scraping moderne permettant d'extraire automatiquement des citations de BrainyQuote.com selon des sujets spécifiés. Le système combine un backend Python robuste avec une interface frontend Nuxt.js, utilisant Supabase comme solution de base de données et de stockage [web:26][web:27].

### 🚀 Fonctionnalités principales

- **Extraction intelligente** : Scraping automatisé avec gestion de pagination
- **Interface moderne** : Frontend Nuxt.js responsive et intuitive
- **Temps réel** : Suivi de progression en direct via WebSockets
- **Stockage cloud** : Base de données Supabase et stockage d'images
- **Export flexible** : Données exportables en CSV/JSON
- **Gestion d'erreurs** : Système robuste avec logging centralisé

## 🏗️ Architecture Technique

### Architecture globale

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │────▶│    Supabase     │
│   (Nuxt.js)     │     │   (FastAPI)     │     │  (PostgreSQL)   │
│                 │     │                 │     │                 │
│ - Interface     │     │ - Playwright    │     │ - Données       │
│ - WebSockets    │     │ - Scraping      │     │ - Images        │
│ - Export CSV    │     │ - API REST      │     │ - Auth          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Stack technique

#### Backend
- **Langage** : Python 3.9+
- **Framework** : FastAPI (API REST haute performance)
- **Scraping** : Playwright (automatisation navigateur)
- **Base de données** : Supabase (PostgreSQL managed)
- **Stockage** : Supabase Storage
- **Communication** : WebSockets pour temps réel

#### Frontend
- **Framework** : Nuxt.js 3 avec TypeScript
- **UI** : Tailwind CSS + Headless UI
- **État** : Pinia stores
- **Communication** : Axios + Socket.io-client
- **Build** : Vite (intégré Nuxt 3)

## 📁 Structure de Projet Optimale

### Structure monorepo recommandée [web:21][web:23]

```
brainyquote-scraper/
├── 📄 README.md                    # Documentation principale
├── 📄 PROJECT.md                   # Ce fichier
├── 📄 .gitignore                   # Ignore files
├── 📄 docker-compose.yml           # Orchestration containers
├── 📄 .env.example                 # Variables d'environnement
│
├── 📂 frontend/                    # Application Nuxt.js
│   ├── 📂 components/
│   │   ├── 📂 ui/                  # Composants UI réutilisables
│   │   │   ├── Button.vue
│   │   │   ├── Input.vue
│   │   │   ├── Modal.vue
│   │   │   └── ProgressBar.vue
│   │   ├── 📂 forms/               # Composants formulaires
│   │   │   ├── TopicForm.vue
│   │   │   └── ExportForm.vue
│   │   ├── 📂 scraping/            # Composants spécifiques scraping
│   │   │   ├── ScrapingStatus.vue
│   │   │   ├── QuotesList.vue
│   │   │   └── ProgressIndicator.vue
│   │   └── 📂 layout/              # Composants layout
│   │       ├── Header.vue
│   │       ├── Footer.vue
│   │       └── Sidebar.vue
│   ├── 📂 pages/                   # Pages Nuxt
│   │   ├── index.vue               # Page principale
│   │   ├── results.vue             # Affichage résultats
│   │   └── history.vue             # Historique scraping
│   ├── 📂 layouts/                 # Layouts globaux
│   │   └── default.vue
│   ├── 📂 stores/                  # Pinia stores
│   │   ├── scraping.ts             # État scraping
│   │   ├── quotes.ts               # Gestion citations
│   │   └── ui.ts                   # État interface
│   ├── 📂 composables/             # Composables Vue
│   │   ├── useScraping.ts          # Logique scraping
│   │   ├── useWebSocket.ts         # WebSocket client
│   │   ├── useSupabase.ts          # Client Supabase
│   │   └── useExport.ts            # Export données
│   ├── 📂 plugins/                 # Plugins Nuxt
│   │   ├── supabase.client.ts
│   │   └── socket.client.ts
│   ├── 📂 middleware/              # Middlewares
│   │   └── auth.ts
│   ├── 📂 types/                   # Types TypeScript
│   │   ├── scraping.ts
│   │   ├── quotes.ts
│   │   └── api.ts
│   ├── 📂 utils/                   # Utilitaires
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   ├── 📂 assets/                  # Assets statiques
│   │   ├── 📂 css/
│   │   ├── 📂 images/
│   │   └── 📂 icons/
│   ├── 📄 nuxt.config.ts           # Configuration Nuxt
│   ├── 📄 tailwind.config.js       # Configuration Tailwind
│   ├── 📄 package.json
│   └── 📄 tsconfig.json
│
├── 📂 backend/                     # Application FastAPI
│   ├── 📂 src/
│   │   ├── 📂 core/                # Configuration centrale
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Variables configuration
│   │   │   ├── logger.py           # Configuration logging
│   │   │   └── exceptions.py       # Exceptions personnalisées
│   │   ├── 📂 models/              # Modèles de données
│   │   │   ├── __init__.py
│   │   │   ├── quote.py            # Modèle Citation
│   │   │   ├── scraping_job.py     # Modèle Job scraping
│   │   │   └── user.py             # Modèle Utilisateur
│   │   ├── 📂 schemas/             # Schémas Pydantic
│   │   │   ├── __init__.py
│   │   │   ├── quote.py            # Schémas citations
│   │   │   ├── scraping.py         # Schémas scraping
│   │   │   └── common.py           # Schémas communs
│   │   ├── 📂 services/            # Services métier
│   │   │   ├── __init__.py
│   │   │   ├── scraper_service.py  # Logique scraping
│   │   │   ├── database_service.py # Interactions DB
│   │   │   ├── storage_service.py  # Gestion fichiers
│   │   │   └── export_service.py   # Export données
│   │   ├── 📂 scraper/             # Module scraping
│   │   │   ├── __init__.py
│   │   │   ├── brainyquote.py      # Scraper BrainyQuote
│   │   │   ├── browser.py          # Gestion navigateur
│   │   │   ├── extractor.py        # Extraction données
│   │   │   └── utils.py            # Utilitaires scraping
│   │   ├── 📂 api/                 # Endpoints API
│   │   │   ├── __init__.py
│   │   │   ├── router.py           # Router principal
│   │   │   ├── 📂 v1/              # Version 1 API
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scraping.py     # Endpoints scraping
│   │   │   │   ├── quotes.py       # Endpoints citations
│   │   │   │   └── export.py       # Endpoints export
│   │   │   └── dependencies.py     # Dépendances API
│   │   ├── 📂 database/            # Base de données
│   │   │   ├── __init__.py
│   │   │   ├── connection.py       # Connexion Supabase
│   │   │   ├── repositories/       # Repositories
│   │   │   │   ├── __init__.py
│   │   │   │   ├── quote_repo.py
│   │   │   │   └── job_repo.py
│   │   │   └── migrations/         # Migrations SQL
│   │   ├── 📂 websocket/           # WebSocket manager
│   │   │   ├── __init__.py
│   │   │   ├── manager.py          # Gestionnaire connexions
│   │   │   └── events.py           # Types d'événements
│   │   ├── 📂 utils/               # Utilitaires backend
│   │   │   ├── __init__.py
│   │   │   ├── validators.py
│   │   │   ├── formatters.py
│   │   │   └── helpers.py
│   │   └── 📄 main.py              # Point d'entrée FastAPI
│   ├── 📂 tests/                   # Tests backend
│   │   ├── __init__.py
│   │   ├── 📂 unit/
│   │   │   ├── test_scraper.py
│   │   │   ├── test_services.py
│   │   │   └── test_utils.py
│   │   ├── 📂 integration/
│   │   │   ├── test_api.py
│   │   │   └── test_database.py
│   │   └── 📂 e2e/
│   │       └── test_full_workflow.py
│   ├── 📂 scripts/                 # Scripts utilitaires
│   │   ├── setup_db.py
│   │   ├── seed_data.py
│   │   └── migrate.py
│   ├── 📄 requirements.txt         # Dépendances Python
│   ├── 📄 requirements-dev.txt     # Dépendances développement
│   ├── 📄 Dockerfile              # Image Docker backend
│   └── 📄 .env.example            # Variables environnement
│
├── 📂 shared/                      # Code partagé
│   ├── 📂 types/                   # Types partagés
│   │   ├── quote.ts
│   │   └── api.ts
│   ├── 📂 constants/               # Constantes partagées
│   │   └── scraping.ts
│   └── 📂 utils/                   # Utilitaires partagés
│       └── validation.ts
│
├── 📂 database/                    # Schémas base de données
│   ├── 📂 migrations/              # Migrations Supabase
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_indexes.sql
│   │   └── 003_add_jobs_table.sql
│   ├── 📂 seeds/                   # Données test
│   │   └── sample_quotes.sql
│   └── 📄 schema.sql               # Schéma complet
│
├── 📂 docs/                        # Documentation
│   ├── 📄 api.md                   # Documentation API
│   ├── 📄 deployment.md            # Guide déploiement
│   ├── 📄 development.md           # Guide développement
│   ├── 📄 architecture.md          # Architecture détaillée
│   └── 📂 assets/                  # Assets documentation
│       └── 📂 images/
│
├── 📂 deploy/                      # Scripts déploiement
│   ├── 📄 docker-compose.prod.yml
│   ├── 📂 kubernetes/              # Manifestes K8s
│   ├── 📂 terraform/               # Infrastructure IaC
│   └── 📂 github-actions/          # Workflows CI/CD
│       ├── 📄 frontend.yml
│       ├── 📄 backend.yml
│       └── 📄 e2e-tests.yml
│
└── 📂 tools/                       # Outils développement
    ├── 📂 scripts/                 # Scripts utilitaires
    │   ├── setup.sh
    │   ├── test.sh
    │   └── build.sh
    └── 📂 configs/                 # Configurations outils
        ├── eslint.config.js
        ├── prettier.config.js
        └── pytest.ini
```

## 🗄️ Schéma de Base de Données

### Tables Supabase

```
-- Table des citations
CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    topic VARCHAR(100) NOT NULL,
    source_url VARCHAR(500),
    image_url VARCHAR(500),
    image_path VARCHAR(500),  -- Chemin Supabase Storage
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Index pour recherche optimisée
    UNIQUE(author, text, topic)
);

-- Table des jobs de scraping
CREATE TABLE scraping_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    total_quotes INTEGER DEFAULT 0,
    processed_quotes INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des utilisateurs (optionnel, pour authentification future)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX idx_quotes_topic ON quotes(topic);
CREATE INDEX idx_quotes_author ON quotes(author);
CREATE INDEX idx_quotes_created_at ON quotes(created_at);
CREATE INDEX idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX idx_scraping_jobs_created_at ON scraping_jobs(created_at);
```

### Bucket Supabase Storage

```
-- Bucket pour images de citations
INSERT INTO storage.buckets (id, name, public)
VALUES ('quote-images', 'quote-images', true);

-- Politique d'accès lecture publique
CREATE POLICY "Public Access" ON storage.objects
FOR SELECT USING (bucket_id = 'quote-images');

-- Politique d'écriture pour service
CREATE POLICY "Service Upload" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'quote-images');
```

## ⚙️ Configuration Détaillée

### Configuration Backend (.env)

```
# FastAPI
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,https://yourapp.vercel.app

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Playwright
PLAYWRIGHT_BROWSERS_PATH=/usr/lib/playwright
PLAYWRIGHT_HEADLESS=True
PLAYWRIGHT_TIMEOUT=30000

# Scraping
MAX_CONCURRENT_PAGES=3
REQUEST_DELAY=1000
RETRY_ATTEMPTS=3
RETRY_DELAY=2000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log

# Redis (pour cache/queues futures)
REDIS_URL=redis://localhost:6379

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Configuration Frontend (nuxt.config.ts)

```
export default defineNuxtConfig({
  // Développement
  devtools: { enabled: true },
  typescript: { typeCheck: true },

  // Modules
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxtjs/color-mode'
  ],

  // CSS Framework
  css: ['~/assets/css/main.css'],

  // Variables d'environnement publiques
  runtimeConfig: {
    // Privées (côté serveur)
    supabaseServiceKey: process.env.SUPABASE_SERVICE_ROLE_KEY,

    // Publiques (côté client)
    public: {
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseAnonKey: process.env.SUPABASE_ANON_KEY,
      apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
      wsUrl: process.env.WS_URL || 'ws://localhost:8000/ws'
    }
  },

  // Configuration build
  nitro: {
    preset: 'vercel' // ou 'netlify', 'node-server'
  },

  // Proxy API pour développement
  nitro: {
    devProxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

## 🚀 Guide de Démarrage Rapide

### Prérequis système

```
# Versions recommandées
Node.js >= 18.0.0
Python >= 3.9.0
Git >= 2.30.0
Docker >= 20.10.0 (optionnel)
```

### Installation complète

```
# 1. Cloner le repository
git clone https://github.com/Leloucher95/brainyquote-scraper.git
cd brainyquote-scraper

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install

# 3. Setup frontend
cd ../frontend
npm install

# 4. Configuration environnement
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Éditer les fichiers .env avec tes credentials Supabase

# 5. Setup base de données
cd backend
python scripts/setup_db.py

# 6. Lancement développement
# Terminal 1 - Backend
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev

# L'application sera accessible sur http://localhost:3000
```

### Docker (alternative)

```
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    volumes:
      - ./backend:/app
    command: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NUXT_PUBLIC_API_BASE_URL=http://backend:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
    depends_on:
      - backend

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

```
# Lancement avec Docker
docker-compose up -d
```

## 🛠️ Workflow de Développement

### Étapes de développement recommandées [web:23]

1. **Phase Setup** (Jour 1-2)
   - Configuration repository et environnements
   - Setup Supabase projet et schéma DB
   - Configuration outils développement

2. **Phase Backend Core** (Jour 3-7)
   - Développement scraper Playwright
   - Intégration Supabase (DB + Storage)
   - API FastAPI et WebSocket

3. **Phase Frontend Core** (Jour 8-12)
   - Interface Nuxt.js et composants
   - Intégration API et temps réel
   - Export et gestion erreurs

4. **Phase Tests & Polish** (Jour 13-15)
   - Tests unitaires et intégration
   - Optimisation performance
   - Documentation et déploiement

### Branching Strategy - Trunk-based Development [web:23]

```
main (trunk)
├── feature/scraper-core
├── feature/frontend-ui
├── feature/realtime-progress
└── hotfix/scraping-timeout
```

**Règles :**
- Branches courtes (max 2-3 jours)
- Pull requests obligatoires
- Tests automatisés sur chaque PR
- Déploiement automatique depuis main

### Scripts de développement

```
// package.json scripts recommandés
{
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd backend && uvicorn src.main:app --reload",
    "dev:frontend": "cd frontend && npm run dev",
    "test": "npm run test:backend && npm run test:frontend",
    "test:backend": "cd backend && pytest",
    "test:frontend": "cd frontend && npm run test",
    "build": "npm run build:backend && npm run build:frontend",
    "build:backend": "cd backend && docker build -t brainyquote-backend .",
    "build:frontend": "cd frontend && npm run build",
    "lint": "npm run lint:backend && npm run lint:frontend",
    "lint:backend": "cd backend && flake8 src/",
    "lint:frontend": "cd frontend && eslint .",
    "format": "npm run format:backend && npm run format:frontend",
    "format:backend": "cd backend && black src/",
    "format:frontend": "cd frontend && prettier --write ."
  }
}
```

## 📊 Gestion des Performances

### Optimisations Scraping

```
# backend/src/scraper/browser.py
class OptimizedBrowser:
    def __init__(self):
        self.browser_config = {
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        }

    async def create_context(self):
        return await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (compatible; ScraperBot/1.0)'
        )
```

### Cache et Optimisations Frontend

```
// frontend/composables/useCache.ts
export const useCache = () => {
  const cache = new Map()

  const getCachedQuotes = (topic: string) => {
    return cache.get(topic)
  }

  const setCachedQuotes = (topic: string, quotes: Quote[]) => {
    cache.set(topic, {
      data: quotes,
      timestamp: Date.now(),
      ttl: 300000 // 5 minutes
    })
  }

  return { getCachedQuotes, setCachedQuotes }
}
```

## 🔐 Sécurité et Bonnes Pratiques

### Sécurité Backend

```
# backend/src/core/security.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_api_key(token: str = Security(security)):
    if token.credentials != settings.API_SECRET_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return token.credentials
```

### Variables d'environnement sécurisées [web:27]

```
# Production uniquement - Ne jamais commiter
SUPABASE_SERVICE_ROLE_KEY=xxxx
API_SECRET_KEY=xxxx
SENTRY_DSN=xxxx

# Développement
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx  # Clé publique, OK
```

## 🚀 Déploiement Production

### Options de déploiement recommandées [web:27]

#### 1. Vercel (Recommandé pour MVP)
```
# Frontend
npx vercel --prod

# Backend (Vercel Functions)
# Structure spécifique requise dans /api
```

#### 2. Railway/Render
```
# railway.toml
[build]
builder = "nixpacks"

[deploy]
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10
```

#### 3. Docker + VPS
```
# backend/Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    chromium \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### CI/CD GitHub Actions

```
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements.txt
          pytest

      - name: Test Frontend
        run: |
          cd frontend
          npm install
          npm run test

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        uses: railway/actions@v1
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Vercel
        uses: vercel/actions@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
```

## 🧪 Stratégie de Tests

### Tests Backend (Pytest)

```
# backend/tests/test_scraper.py
import pytest
from src.scraper.brainyquote import BrainyQuoteScraper

@pytest.mark.asyncio
async def test_scraper_extract_quotes():
    scraper = BrainyQuoteScraper()
    quotes = await scraper.scrape_topic("motivation", limit=5)

