from typing import Final

from my_modules import kubernetes as k8s


POSTGRES_CONFIGMAP = k8s.get_json("postgres-configmap", "configmap")
POSTGRES_SECRET = k8s.get_json("postgres-auth-secret", "secret", base64decode=True)


POSTGRES_USERNAME = POSTGRES_SECRET.get("username", "seshu")
POSTGRES_PASSWORD = POSTGRES_SECRET.get("password", "1234")
POSTGRES_HOST = POSTGRES_CONFIGMAP.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = POSTGRES_CONFIGMAP.get("POSTGRES_PORT", "5432")
POSTGRES_DB = POSTGRES_CONFIGMAP.get("POSTGRES_DB", "database")


# sqlalchemy connection string for postgres db
connection_string: Final[str] = (
    f"postgresql+psycopg2://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
