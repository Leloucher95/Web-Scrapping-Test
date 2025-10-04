# Configuration Supabase pour BrainyQuote Scraper

Ce guide vous explique comment configurer Supabase pour stocker les citations et images extraites.

## 📋 Prérequis

1. Compte Supabase gratuit : [https://supabase.com](https://supabase.com)
2. Python avec les dépendances installées
3. Citations déjà extraites par le scraper

## 🚀 Configuration étape par étape

### 1. Créer un projet Supabase

1. Connectez-vous à [Supabase Dashboard](https://app.supabase.com)
2. Cliquez sur "New Project"
3. Choisissez votre organisation
4. Donnez un nom à votre projet (ex: "brainyquote-scraper")
5. Créez un mot de passe sécurisé pour la base de données
6. Choisissez une région proche de vous
7. Cliquez sur "Create new project"

### 2. Configurer la base de données

1. Allez dans l'onglet "SQL Editor" de votre projet Supabase
2. Copiez le contenu du fichier `database/enhanced_supabase_setup.sql`
3. Collez-le dans l'éditeur SQL et exécutez le script
4. Vérifiez que les tables sont créées dans l'onglet "Table Editor"

### 3. Configurer le stockage d'images

1. Allez dans l'onglet "Storage"
2. Cliquez sur "Create a new bucket"
3. Nom du bucket : `quote-images`
4. Cochez "Public bucket" pour permettre l'accès public aux images
5. Cliquez sur "Create bucket"

### 4. Récupérer les clés API

1. Allez dans l'onglet "Settings" > "API"
2. Copiez les valeurs suivantes :
   - **Project URL** (URL)
   - **anon public** (Clé publique/anonyme)

### 5. Configurer les variables d'environnement

1. Créez un fichier `.env` dans le dossier `backend/` :
```bash
# Remplacez par vos vraies valeurs
SUPABASE_URL=https://votre-project-id.supabase.co
SUPABASE_ANON_KEY=votre-cle-anon-key-ici
```

2. **⚠️ Important** : Ajoutez `.env` à votre `.gitignore` pour ne pas exposer vos clés

## 🧪 Tester la configuration

### Test rapide de connexion
```bash
cd backend
source venv_new/bin/activate
python src/main_supabase.py
```

### Fonctionnalités disponibles

Le système complet offre :

- ✅ **Extraction** de citations avec métadonnées complètes
- ✅ **Stockage** dans Supabase avec schéma optimisé
- ✅ **Upload d'images** dans Supabase Storage
- ✅ **Recherche** full-text dans les citations
- ✅ **Statistiques** et analyses
- ✅ **API REST** automatique via Supabase

### Structure des données

**Table `quotes`** :
- `id` : UUID unique
- `text` : Texte de la citation
- `author` : Nom de l'auteur
- `source_url` : URL source BrainyQuote
- `image_url` : URL originale de l'image
- `supabase_image_url` : URL Supabase de l'image
- `category` : Catégorie (motivational, love, success, etc.)
- `extracted_at` : Date d'extraction
- `metadata` : Métadonnées JSON supplémentaires

## 📊 Exemples d'utilisation

### Rechercher des citations
```sql
SELECT * FROM search_quotes('motivation');
```

### Obtenir des citations aléatoires
```sql
SELECT * FROM get_random_quotes(5);
```

### Statistiques
```sql
SELECT * FROM quote_statistics;
```

### Top auteurs
```sql
SELECT * FROM top_authors LIMIT 10;
```

## 🔧 Dépannage

### Erreur de connexion
- Vérifiez vos URL et clés dans le fichier `.env`
- Assurez-vous que le projet Supabase est actif

### Erreur de stockage
- Vérifiez que le bucket `quote-images` existe
- Vérifiez que le bucket est public

### Erreur de permissions
- Exécutez le script SQL `enhanced_supabase_setup.sql`
- Vérifiez les politiques RLS dans l'onglet "Authentication" > "Policies"

## 🎯 Prochaines étapes

Une fois Supabase configuré, vous pouvez :

1. **Extraire et stocker** des citations en masse
2. **Développer une API** FastAPI pour accéder aux données
3. **Créer un frontend** Nuxt.js pour afficher les citations
4. **Implémenter des fonctionnalités** de recherche et filtrage avancées

## 📚 Ressources

- [Documentation Supabase](https://supabase.com/docs)
- [Guide API Supabase](https://supabase.com/docs/guides/api)
- [Documentation Storage](https://supabase.com/docs/guides/storage)