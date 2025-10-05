# 📚 Documentation Complète - QuoteScrape

> Application de web scraping automatisée pour extraire des citations depuis BrainyQuote.com

**Version:** 1.0.0 | **Date:** 5 octobre 2025 | **Statut:** ✅ Production Ready

---

## 📑 Table des Matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture](#2-architecture)
3. [Installation](#3-installation)
4. [Configuration](#4-configuration)
5. [Utilisation](#5-utilisation)
6. [API Reference](#6-api-reference)
7. [Développement](#7-développement)
8. [Dépannage](#8-dépannage)
9. [Déploiement](#9-déploiement)
10. [Maintenance](#10-maintenance)

---

## 1. Vue d'ensemble

### Qu'est-ce que QuoteScrape?

Application full-stack qui automatise l'extraction de citations depuis BrainyQuote.com avec:
- ✅ Scraping robuste (Playwright + anti-détection)
- ✅ Extraction complète sans limite
- ✅ Stockage Supabase (Database + Images)
- ✅ Interface moderne (Nuxt.js + TypeScript)
- ✅ Temps réel (WebSocket)

### Technologies

| Stack | Technologies |
|-------|-------------|
| **Backend** | Python 3.10+, FastAPI 0.118, Playwright 1.55 |
| **Frontend** | Nuxt.js 4.1, TypeScript 5.x, TailwindCSS |
| **Database** | Supabase (PostgreSQL) |
| **Storage** | Supabase Storage |
| **Real-time** | WebSocket |

### Fonctionnalités clés

**Backend:**
- Web scraping avec pagination automatique
- Mode "Extraire TOUTES les citations"
- Téléchargement automatique des images
- API REST complète
- WebSocket pour mises à jour temps réel
- Arrêt gracieux
- Logging détaillé

**Frontend:**
- Interface responsive moderne
- Formulaire de configuration
- Progression temps réel
- Export CSV/JSON
- Visualisation interactive

---

## 2. Architecture

### Diagramme

```
User Browser (3000) → Nuxt.js Frontend
                          ↓
                     API/WebSocket
                          ↓
                   FastAPI Backend (8000)
                    ↙              ↘
          Playwright          Supabase Cloud
          (BrainyQuote)       (DB + Storage)
```

### Flux de données

```
1. User → Submit form
2. Backend → Start scraping task
3. Playwright → Navigate & extract quotes
4. Backend → Store in Supabase
5. WebSocket → Broadcast progress
6. Frontend → Display real-time updates
7. User → Export data (CSV/JSON)
```

---

## 3. Installation

### Prérequis

```bash
# Vérifier les versions
python3 --version  # 3.10+
node --version     # 18.0+
npm --version      # 8.0+
```

### Backend

```bash
cd backend

# Environnement virtuel
python3 -m venv venv_new
source venv_new/bin/activate

# Dépendances
pip install -r requirements.txt
playwright install chromium

# Vérification
python -c "import playwright, fastapi, supabase; print('✅ OK')"
```

### Frontend

```bash
cd frontend/QuoteScrape

# Installation
npm install  # ou pnpm install

# Vérification
npm run build
```

### Supabase

```bash
# 1. Créer projet sur supabase.com
# 2. Aller dans SQL Editor
# 3. Exécuter: backend/database/enhanced_supabase_setup.sql
```

---

## 4. Configuration

### Backend `.env`

```bash
# backend/.env
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=60000
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...  # ⚠️ Secret!
```

### Frontend `.env.local`

```bash
# frontend/QuoteScrape/.env.local
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
NUXT_PUBLIC_WS_URL=ws://localhost:8000
NUXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NUXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

---

## 5. Utilisation

### Démarrage

```bash
# Terminal 1 - Backend
cd backend
./start-backend.sh

# Terminal 2 - Frontend
cd frontend/QuoteScrape
npm run dev
```

### Interface (http://localhost:3000)

1. **Choisir un sujet**: Motivational, Success, Love, etc.
2. **Mode extraction**:
   - ❌ Limité (slider 1-200)
   - ✅ TOUTES les citations
3. **Options**: Images, Database
4. **Lancer** et suivre la progression
5. **Exporter** CSV/JSON

---

## 6. API Reference

### Endpoints

#### POST /api/scrape/start

```json
{
  "topic": "success",
  "max_quotes": 10,  // null = ALL
  "include_images": true,
  "store_in_database": true
}
```

#### POST /api/scrape/stop
```json
{ "success": true, "message": "Stop requested" }
```

#### GET /api/scrape/status
```json
{
  "status": "running",
  "progress": { "current": 5, "total": 10 },
  "stats": { "extracted": 5, "images": 5, "errors": 0 }
}
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/scraping');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Types: status, progress, quote_extracted, completed, stopped
};
```

---

## 7. Développement

### Structure

```
backend/src/
├── main.py                    # FastAPI app
├── scraper/
│   └── brainyquote_hybrid.py  # Scraper
└── database/
    └── supabase_storage.py    # DB operations

frontend/app/
├── pages/index.vue            # Main page
├── stores/scraping.ts         # Pinia store
└── components/scraping/       # Components
```

### Ajouter un sujet

Frontend seulement:
```vue
<option value="nouveau">Nouveau Sujet</option>
```

### Modifier les sélecteurs

Si BrainyQuote change:
```python
# brainyquote_hybrid.py ligne ~258
selectors_to_try = [
    '.bqQt',  # Actuel
    '.new-selector',  # Ajouter
]
```

---

## 8. Dépannage

### Problèmes courants

| Erreur | Solution |
|--------|----------|
| `Module 'main_supabase' not found` | Utiliser `uvicorn main:app` |
| `WebSocket 403` | URL: `ws://localhost:8000` (sans /ws) |
| `Browser not found` | `playwright install chromium` |
| `Supabase 401` | Vérifier clés dans .env |
| CORS error | Backend doit tourner sur 8000 |

### Diagnostic

```bash
# Vérifier processus
ps aux | grep uvicorn
ps aux | grep node

# Tester API
curl http://localhost:8000/health

# Logs
tail -f backend/src/*.log
```

---



