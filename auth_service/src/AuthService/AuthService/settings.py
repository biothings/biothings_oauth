import os


# Tornado settings
DEBUG = int(os.environ.get("DEBUG", default=0))

# Database connection settings
DB_ENGINE = os.environ.get("DB_ENGINE")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# SQLAlchemy settings
SQLALCHEMY_DB_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@" \
                    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
