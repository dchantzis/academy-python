"""In-memory SQLite engine for isolated learning, not the JamesDoe PostgreSQL engine."""
from sqlalchemy import create_engine, text
engine = create_engine("sqlite+pysqlite:///:memory:")
with engine.connect() as connection:
    print(connection.execute(text("SELECT 1")).scalar_one())
