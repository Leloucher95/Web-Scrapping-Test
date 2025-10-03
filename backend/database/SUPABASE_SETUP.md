# Configuration Supabase pour BrainyQuote Scraper

## Étapes de configuration

### 1. Créer un projet Supabase
1. Allez sur [supabase.com](https://supabase.com)
2. Créez un compte ou connectez-vous
3. Créez un nouveau projet
4. Notez l'URL du projet et les clés API

### 2. Récupérer les clés d'API
Dans le dashboard Supabase, allez dans **Settings > API** :

- **Project URL** : `https://your-project-ref.supabase.co`
- **anon/public key** : Clé pour les opérations client
- **service_role key** : Clé pour les opérations serveur (gardez-la secrète)

### 3. Configurer le fichier .env
Copiez vos clés dans `/backend/.env` :

```bash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Créer les tables
1. Allez dans **SQL Editor** dans le dashboard Supabase
2. Copiez le contenu du fichier `database/supabase_setup.sql`
3. Exécutez le script SQL

### 5. Vérifier les tables créées
Allez dans **Table Editor** et vérifiez que vous avez :
- `scraping_jobs` - Table des jobs de scraping
- `quotes` - Table des citations
- La vue `job_statistics` pour les statistiques

### 6. Configuration des politiques de sécurité (optionnel)
Pour un environnement de production, configurez RLS (Row Level Security) :
- Activez RLS sur les tables
- Créez des politiques pour contrôler l'accès aux données

### 7. Test de la connexion
Une fois configuré, vous pouvez tester avec :
```bash
cd /home/juste/Work/Web-Scrapping-Test/backend
source venv/bin/activate
python -c "from src.database.supabase import supabase_client; print('Connexion Supabase OK')"
```

## Structure des tables

### Table `scraping_jobs`
- `id` (UUID, Primary Key)
- `topic` (VARCHAR) - Sujet à scraper
- `status` (VARCHAR) - État du job (pending, running, completed, failed, stopped)
- `user_id` (UUID, Nullable) - ID utilisateur
- `total_quotes` (INTEGER) - Nombre total de citations trouvées
- `processed_quotes` (INTEGER) - Nombre de citations traitées
- `error_message` (TEXT, Nullable) - Message d'erreur
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Table `quotes`
- `id` (UUID, Primary Key)
- `job_id` (UUID, Foreign Key) - Référence vers scraping_jobs
- `text` (TEXT) - Texte de la citation
- `author` (VARCHAR) - Nom de l'auteur
- `link` (TEXT, Nullable) - Lien vers la citation
- `image_url` (TEXT, Nullable) - URL de l'image de l'auteur
- `created_at` (TIMESTAMP)

## API Endpoints disponibles
Une fois configuré, les endpoints suivants seront disponibles :
- `POST /api/scrape/start` - Démarrer un scraping
- `GET /api/scrape/status/{job_id}` - État d'un job
- `POST /api/scrape/stop/{job_id}` - Arrêter un job
- `GET /api/jobs` - Liste des jobs
- `GET /api/quotes/{job_id}` - Citations d'un job
- `GET /api/jobs/{job_id}/statistics` - Statistiques d'un job
- `POST /api/jobs/{job_id}/export` - Exporter les données
- `DELETE /api/jobs/{job_id}` - Supprimer un job