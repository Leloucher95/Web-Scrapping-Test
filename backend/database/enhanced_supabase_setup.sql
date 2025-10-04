-- Enhanced Supabase Setup for BrainyQuote Scraper
-- This script creates the necessary tables and storage for the quote scraping application

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create quotes table with comprehensive schema
CREATE TABLE IF NOT EXISTS quotes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    text TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    source_url TEXT,
    image_url TEXT,
    supabase_image_url TEXT,
    category VARCHAR(100) DEFAULT 'general',
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',

    -- Constraints
    CONSTRAINT quotes_text_not_empty CHECK (char_length(text) > 0),
    CONSTRAINT quotes_author_not_empty CHECK (char_length(author) > 0)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_quotes_author ON quotes(author);
CREATE INDEX IF NOT EXISTS idx_quotes_category ON quotes(category);
CREATE INDEX IF NOT EXISTS idx_quotes_extracted_at ON quotes(extracted_at DESC);
CREATE INDEX IF NOT EXISTS idx_quotes_text_search ON quotes USING gin(to_tsvector('english', text));
CREATE INDEX IF NOT EXISTS idx_quotes_author_search ON quotes USING gin(to_tsvector('english', author));

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_quotes_updated_at ON quotes;
CREATE TRIGGER update_quotes_updated_at
    BEFORE UPDATE ON quotes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create authors table for normalization (optional)
CREATE TABLE IF NOT EXISTS authors (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT,
    birth_date DATE,
    death_date DATE,
    nationality VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default categories
INSERT INTO categories (name, description) VALUES
    ('motivational', 'Motivational and inspirational quotes'),
    ('love', 'Quotes about love and relationships'),
    ('success', 'Quotes about success and achievement'),
    ('wisdom', 'Wise and philosophical quotes'),
    ('life', 'Quotes about life and living'),
    ('happiness', 'Quotes about happiness and joy'),
    ('general', 'General quotes without specific category')
ON CONFLICT (name) DO NOTHING;

-- Row Level Security policies for quotes table
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;

-- Allow anyone to read quotes
CREATE POLICY "Anyone can read quotes" ON quotes
    FOR SELECT TO public USING (true);

-- Allow authenticated users to insert quotes
CREATE POLICY "Authenticated users can insert quotes" ON quotes
    FOR INSERT TO authenticated WITH CHECK (true);

-- Allow authenticated users to update their own quotes
CREATE POLICY "Users can update quotes" ON quotes
    FOR UPDATE TO authenticated USING (true);

-- Create a view for quote statistics
CREATE OR REPLACE VIEW quote_statistics AS
SELECT
    COUNT(*) as total_quotes,
    COUNT(DISTINCT author) as unique_authors,
    COUNT(CASE WHEN supabase_image_url IS NOT NULL THEN 1 END) as quotes_with_images,
    COUNT(CASE WHEN category = 'motivational' THEN 1 END) as motivational_quotes,
    COUNT(CASE WHEN category = 'love' THEN 1 END) as love_quotes,
    COUNT(CASE WHEN category = 'success' THEN 1 END) as success_quotes,
    MAX(extracted_at) as last_extraction,
    MIN(extracted_at) as first_extraction
FROM quotes;

-- Create a view for top authors
CREATE OR REPLACE VIEW top_authors AS
SELECT
    author,
    COUNT(*) as quote_count,
    MAX(extracted_at) as last_quote_date,
    COUNT(CASE WHEN supabase_image_url IS NOT NULL THEN 1 END) as quotes_with_images
FROM quotes
GROUP BY author
ORDER BY quote_count DESC;

-- Create function to search quotes
CREATE OR REPLACE FUNCTION search_quotes(search_term TEXT)
RETURNS TABLE(
    id UUID,
    text TEXT,
    author VARCHAR(255),
    category VARCHAR(100),
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        q.id,
        q.text,
        q.author,
        q.category,
        ts_rank(to_tsvector('english', q.text || ' ' || q.author), plainto_tsquery('english', search_term)) as rank
    FROM quotes q
    WHERE to_tsvector('english', q.text || ' ' || q.author) @@ plainto_tsquery('english', search_term)
    ORDER BY rank DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function to get random quotes
CREATE OR REPLACE FUNCTION get_random_quotes(limit_count INTEGER DEFAULT 10)
RETURNS TABLE(
    id UUID,
    text TEXT,
    author VARCHAR(255),
    category VARCHAR(100),
    supabase_image_url TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        q.id,
        q.text,
        q.author,
        q.category,
        q.supabase_image_url
    FROM quotes q
    ORDER BY RANDOM()
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT ALL ON quotes TO authenticated;
GRANT ALL ON authors TO authenticated;
GRANT ALL ON categories TO authenticated;
GRANT SELECT ON quote_statistics TO public;
GRANT SELECT ON top_authors TO public;

-- Create indexes for the functions
CREATE INDEX IF NOT EXISTS idx_quotes_random ON quotes(id);

-- Instructions for setup:
-- 1. Run this SQL script in your Supabase SQL editor
-- 2. Create a storage bucket named 'quote-images' with public access
-- 3. Set up your .env file with SUPABASE_URL and SUPABASE_ANON_KEY
-- 4. Install required packages: pip install supabase python-dotenv
-- 5. Test the connection using main_supabase.py