import os


def get_postgres_uri() -> str:
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = 54321 if host == "127.0.0.1" else 5432
    password = os.environ.get("DB_PASSWORD", "abc1234")
    user, db_name = "allocation", "allocation"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url() -> str:
    host = os.environ.get("API_HOST", "127.0.0.1")
    # port = 5005 if host == "localhost" else 80
    port = 5005 if host == "127.0.0.1" else 80
    # port = 5000 if host == "localhost" else 80
    return f"http://{host}:{port}"
