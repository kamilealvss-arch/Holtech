import os

APP_NAME = os.getenv("APP_NAME", "Holtech API")
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")

# ─────────────────────────────────────────────────
# Modo do Banco de Dados
# 0: JSON (arquivo local db.json)
# 1: PostgreSQL
# ─────────────────────────────────────────────────
TIPO_BANCO = int(os.getenv("TIPO_BANCO", "0"))

# ─────────────────────────────────────────────────
# Configurações HTTP
# ─────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]
SERVE_STATIC_FRONTEND = os.getenv("SERVE_STATIC_FRONTEND", "true").lower() in ("1", "true", "yes", "sim")

# ─────────────────────────────────────────────────
# Configurações PostgreSQL
# ─────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "login_holtech")
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "17212931")

# ─────────────────────────────────────────────────
# Caminhos de arquivos e estáticos
# ─────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
JSON_DB_FILE = os.path.join(BASE_DIR, "db.json")

LP_PATH        = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "landing", "public"))
LOGIN_PATH     = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "login"))
CRUD_PATH      = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "admin"))
AUDITORIA_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "auditoria"))
