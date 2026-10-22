import os

# The app reads DATABASE_URL at import and crashes without it. The tests never
# open the pool, so a harmless dummy value is enough (CI has no .env).
os.environ.setdefault("DATABASE_URL", "postgresql://app:unused@localhost:5432/appdb")
