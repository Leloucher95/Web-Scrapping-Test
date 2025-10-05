# 🚀 Guide de Démarrage Rapide - QuoteScrape

## ⏱️ 5 minutes pour commencer

### 1. Installation (2 min)

```bash
# Cloner et installer
git clone <votre-repo>
cd Web-Scrapping-Test

# Backend
cd backend
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt
playwright install chromium

# Frontend
cd ../frontend/QuoteScrape
npm install
```

### 2. Configuration (1 min)

```bash
# Backend .env
cat > backend/.env << EOF
PLAYWRIGHT_HEADLESS=true
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your_key
SUPABASE_SERVICE_KEY=your_key
EOF

# Frontend .env.local
cat > frontend/QuoteScrape/.env.local << EOF
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
NUXT_PUBLIC_WS_URL=ws://localhost:8000
EOF
```

### 3. Démarrage (30 sec)

```bash
# Terminal 1
cd backend
./start-backend.sh

# Terminal 2
cd frontend/QuoteScrape
npm run dev
```

### 4. Utilisation (1 min)

1. Ouvrir http://localhost:3000
2. Choisir un sujet
3. Cocher "Extraire TOUTES les citations"
4. Cliquer "Lancer le scraping"
5. Observer les citations s'afficher en temps réel!

---

## 🎯 Commandes essentielles

```bash
# Démarrer backend
cd backend/src
source ../venv_new/bin/activate
uvicorn main:app --reload

# Démarrer frontend
cd frontend/QuoteScrape
npm run dev

# Tester API
curl http://localhost:8000/health

# Arrêter tout
Ctrl+C (dans chaque terminal)
```

---

## ✅ Checklist

- [ ] Python 3.10+ installé
- [ ] Node.js 18+ installé
- [ ] Compte Supabase créé
- [ ] Backend .env configuré
- [ ] Frontend .env.local configuré
- [ ] Backend démarre sur :8000
- [ ] Frontend démarre sur :3000
- [ ] Premier scraping réussi

---

## 🆘 Problèmes?

| Problème | Solution Express |
|----------|------------------|
| Port 8000 occupé | `kill $(lsof -t -i:8000)` |
| Port 3000 occupé | `kill $(lsof -t -i:3000)` |
| Import error | Vérifier qu'on est dans venv |
| WebSocket 403 | Redémarrer frontend |

---

**Prêt à scraper!** 🎉

Voir [DOCUMENTATION_COMPLETE.md](DOCUMENTATION_COMPLETE.md) pour plus de détails.
