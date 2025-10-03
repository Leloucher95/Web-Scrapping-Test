# 🎯 BrainyQuote Scraper - Plan d'Exécution

## 📋 Cahier des charges (Requirements)

### Description du projet
Web Scraping avec automatisation de navigateur et frontend Nuxt pour extraire des citations de BrainyQuote.com selon un sujet donné par l'utilisateur.

**Site cible** : https://www.brainyquote.com/
**URL Pattern** : https://www.brainyquote.com/topics/{topic}-quotes
**Exemple** : topic "motivational" → https://www.brainyquote.com/topics/motivational-quotes

### Exigences Backend (Python)
- [x] Outil d'automatisation : **Playwright**
- [ ] Extraction des champs obligatoires :
  1. **Nom de l'auteur**
  2. **Texte de la citation**
  3. **Lien de la citation**
- [ ] Stockage **Supabase Database** (schéma approprié)
- [ ] Téléchargement images → **Supabase Storage**
- [ ] Gestion d'erreurs robuste
- [ ] Système de journalisation (logging)

### Exigences Frontend (TypeScript)
- [x] Framework : **Nuxt.js**
- [x] ✅ Formulaire saisie sujet
- [x] ✅ Bouton lancer scraper
- [ ] 🔄 Indicateur progression (items traités)
- [ ] 🔄 Bouton arrêter scraper
- [ ] 🔄 Export CSV/JSON des données
- [x] ✅ Interface responsive et conviviale

### Livrables finaux
- [ ] Code backend scraper + intégration Supabase
- [x] ✅ Frontend Nuxt.js avec UI spécifiée
- [ ] Documentation installation/utilisation/déploiement

## 🏗️ Architecture Technique

### Stack confirmé
- **Backend** : FastAPI + Playwright + Supabase Python Client
- **Frontend** : Nuxt.js 4 + TypeScript + Tailwind + Pinia
- **Database** : Supabase PostgreSQL + Storage
- **Communication** : WebSocket temps réel + REST API

### Structure fichiers cible
```
backend/
├── src/
│   ├── main.py                 # FastAPI app
│   ├── core/
│   │   ├── config.py          # Variables env
│   │   └── logger.py          # Logging setup
│   ├── api/
│   │   ├── router.py          # Routes principales
│   │   └── scraping.py        # Endpoints scraping
│   ├── scraper/
│   │   ├── brainyquote.py     # Scraper BrainyQuote
│   │   └── browser.py         # Gestion Playwright
│   ├── database/
│   │   ├── connection.py      # Supabase client
│   │   └── models.py          # Schémas DB
│   └── websocket/
│       └── manager.py         # WebSocket manager
├── requirements.txt
└── .env.example
```

## 📊 Schéma Base de Données

### Table `quotes`
```sql
CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    link VARCHAR(500) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    image_url VARCHAR(500),        -- URL image BrainyQuote
    image_path VARCHAR(500),       -- Chemin Supabase Storage
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(author, text, topic)    -- Éviter doublons
);
```

### Table `scraping_jobs`
```sql
CREATE TABLE scraping_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed, stopped
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Bucket Supabase Storage
```
Bucket: 'quote-images'
Structure: /topic/author-hash.jpg
Exemple: /motivational/einstein-abc123.jpg
```

## 🚀 Plan d'Exécution

### ✅ Phase 0 : Setup Initial (TERMINÉ)
- [x] Repository Git
- [x] Frontend Nuxt.js structure conforme
- [x] Documentation troubleshooting
- [x] Structure monorepo
- [x] .env frontend

### 🔄 Phase 1 : Backend Core (EN COURS)
**Objectif** : API fonctionnelle + Scraper basique

#### 1.1 Structure FastAPI
- [ ] `backend/src/main.py` - App FastAPI
- [ ] `backend/requirements.txt` - Dependencies
- [ ] `backend/.env.example` - Variables env
- [ ] Endpoints REST :
  - `POST /api/scrape/start` → lance scraping, retourne job_id
  - `POST /api/scrape/stop/{job_id}` → arrête scraping
  - `GET /api/scrape/status/{job_id}` → statut progression
  - `GET /api/quotes?topic={topic}` → récupérer citations
  - `GET /api/export/{job_id}?format=csv|json` → export données

#### 1.2 Scraper Playwright
- [ ] `backend/src/scraper/brainyquote.py` - Logic scraping
- [ ] Gestion URL : `https://www.brainyquote.com/topics/{topic}-quotes`
- [ ] Extraction champs obligatoires :
  - Nom auteur (selector : à identifier)
  - Texte citation (selector : à identifier)
  - Lien citation (href)
- [ ] Gestion pagination (BrainyQuote → pages multiples)
- [ ] Download images vers Supabase Storage

#### 1.3 Intégration Supabase
- [ ] `backend/src/database/connection.py` - Client Supabase
- [ ] `backend/src/database/models.py` - Schémas Pydantic
- [ ] Setup tables (quotes, scraping_jobs)
- [ ] Setup bucket Storage 'quote-images'

#### 1.4 WebSocket Manager
- [ ] `backend/src/websocket/manager.py` - Gestion connexions
- [ ] Événements WebSocket :
  - `scraping_started` → {job_id, topic}
  - `progress_update` → {job_id, processed, total}
  - `quote_found` → {job_id, quote_data}
  - `scraping_completed` → {job_id, total_quotes}
  - `scraping_failed` → {job_id, error}
  - `scraping_stopped` → {job_id}

### 🔄 Phase 2 : Frontend Complet (À VENIR)
**Objectif** : Interface finale conforme exigences

#### 2.1 Fonctionnalités manquantes
- [ ] Bouton "Arrêter scraper"
- [ ] Indicateur progression temps réel via WebSocket
- [ ] Affichage citations extraites (temps réel)
- [ ] Export CSV/JSON avec téléchargement
- [ ] Gestion erreurs utilisateur (toasts)

#### 2.2 Plugin WebSocket Frontend
- [ ] `app/plugins/websocket.client.ts` - Connexion auto
- [ ] Mise à jour stores Pinia via événements WS
- [ ] Reconnexion automatique si déconnexion

#### 2.3 Stores Pinia enrichis
- [ ] `app/stores/scraping.ts` - État scraping étendu
- [ ] `app/stores/quotes.ts` - Liste citations + pagination
- [ ] `app/stores/export.ts` - Gestion export fichiers

### 🧪 Phase 3 : Tests & Polish (À VENIR)
- [ ] Tests unitaires scraper (pytest)
- [ ] Tests e2e API (FastAPI TestClient)
- [ ] Tests frontend (Vitest)
- [ ] Documentation complète
- [ ] Docker setup
- [ ] Déploiement guide

## 📝 Notes d'Implémentation

### URLs BrainyQuote à analyser
```
# Explorer ces URLs pour comprendre la structure
https://www.brainyquote.com/topics/motivational-quotes
https://www.brainyquote.com/topics/love-quotes
https://www.brainyquote.com/topics/success-quotes

# Identifier les sélecteurs CSS pour :
- Container citations
- Nom auteur
- Texte citation
- Lien citation
- Image citation (si existe)
- Bouton pagination/Next
```

### Gestion erreurs prioritaires
1. **Sujet inexistant** → Page 404 BrainyQuote
2. **Rate limiting** → Délais entre requêtes
3. **Connexion Supabase** → Retry logic
4. **Images indisponibles** → Fallback gracieux
5. **Scraping interrompu** → Nettoyage état

### Performance considerations
- **Concurrent scraping** : Max 3 jobs simultanés
- **Request delay** : 1-2s entre pages BrainyQuote
- **Batch insert** : Grouper insertions DB
- **Image compression** : Optimiser taille Storage

## 🎯 Critères de Succès

### Fonctionnel
- [x] ✅ Frontend responsive et intuitif
- [ ] 🔄 Scraping complet d'un sujet donné
- [ ] 🔄 Stockage correct DB + Storage
- [ ] 🔄 Export CSV/JSON fonctionnel
- [ ] 🔄 Arrêt scraping mid-process
- [ ] 🔄 Progression temps réel

### Technique
- [ ] 🔄 Code modulaire et maintenable
- [ ] 🔄 Gestion erreurs robuste
- [ ] 🔄 Logging complet
- [ ] 🔄 Documentation installation/usage
- [ ] 🔄 Performance acceptable (< 5s/page)

---

## 🚧 Statut Actuel : Phase 1.1 Backend Structure

**Prochaine action** : Créer structure FastAPI + requirements.txt + premier endpoint de test.