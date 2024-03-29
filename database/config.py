import os

DEFAULT_SECRET_KEY = "13432rtweG"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"
DATABASE_URL = "sqlite+aiosqlite:///./memory_usage.db"
################# AUTHENTICATION #################
JWT_REFRESH_SECRET_KEY = os.environ.get("JWT_REFRESH_SECRET_KEY", DEFAULT_SECRET_KEY)
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", DEFAULT_SECRET_KEY)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # 365 days
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # 365 days
ALGORITHM = "HS256"
################### SERVICE #################
INTERVAL = 60  # 60 seconds
