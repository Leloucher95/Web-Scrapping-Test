-- Script SQL pour créer les tables Supabase nécessaires au projet BrainyQuote Scraper

-- 1. Table pour les jobs de scraping
CREATE TABLE IF NOT EXISTS scraping_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    user_id UUID NULL,
    total_quotes INTEGER DEFAULT 0,
    processed_quotes INTEGER DEFAULT 0,
    error_message TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Table pour les citations extraites
CREATE TABLE IF NOT EXISTS quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES scraping_jobs(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    link TEXT NULL,
    image_url TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_created_at ON scraping_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quotes_job_id ON quotes(job_id);
CREATE INDEX IF NOT EXISTS idx_quotes_author ON quotes(author);
CREATE INDEX IF NOT EXISTS idx_quotes_created_at ON quotes(created_at DESC);

-- 4. Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_scraping_jobs_updated_at BEFORE UPDATE
    ON scraping_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 5. RLS (Row Level Security) - Optionnel pour multi-utilisateurs
-- ALTER TABLE scraping_jobs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;

-- Politique pour permettre à tous les utilisateurs de lire/écrire (pour développement)
-- CREATE POLICY "Allow all operations for authenticated users" ON scraping_jobs
--     FOR ALL USING (auth.role() = 'authenticated');

-- CREATE POLICY "Allow all operations for authenticated users" ON quotes
--     FOR ALL USING (auth.role() = 'authenticated');

-- 6. Bucket pour le stockage d'images (si nécessaire)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('quote-images', 'quote-images', true);

-- 7. Vues utiles pour les statistiques
CREATE OR REPLACE VIEW job_statistics AS
SELECT
    sj.id,
    sj.topic,
    sj.status,
    sj.created_at,
    sj.updated_at,
    COUNT(q.id) as actual_quotes_count,
    sj.total_quotes as reported_quotes_count,
    EXTRACT(EPOCH FROM (COALESCE(sj.updated_at, NOW()) - sj.created_at)) as duration_seconds
FROM scraping_jobs sj
LEFT JOIN quotes q ON sj.id = q.job_id
GROUP BY sj.id, sj.topic, sj.status, sj.created_at, sj.updated_at, sj.total_quotes
ORDER BY sj.created_at DESC;