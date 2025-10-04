"""import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))

    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")  # For client operations
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # Playwright Configuration
    PLAYWRIGHT_HEADLESS: bool = os.getenv("PLAYWRIGHT_HEADLESS", "True").lower() == "true"
    PLAYWRIGHT_TIMEOUT: int = int(os.getenv("PLAYWRIGHT_TIMEOUT", 30000))

    # Scraping Configuration
    MAX_CONCURRENT_PAGES: int = int(os.getenv("MAX_CONCURRENT_PAGES", 3))
    REQUEST_DELAY: int = int(os.getenv("REQUEST_DELAY", 1000))
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", 3))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
"""
# src/core/config.py
import os
from pathlib import Path

class Settings:
    """Configuration de l'application"""

    # Playwright settings
    PLAYWRIGHT_HEADLESS = True
    PLAYWRIGHT_TIMEOUT = 30000

    # Scraping settings
    MAX_QUOTES_PER_TOPIC = 50
    REQUEST_DELAY = 1  # secondes entre les requêtes

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "scraping.log"

    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    SCREENSHOTS_DIR = BASE_DIR / "screenshots"

    def __init__(self):
        # Créer les dossiers nécessaires
        self.SCREENSHOTS_DIR.mkdir(exist_ok=True)

settings = Settings()
