from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=True,   # reconnect automatically if connection was dropped
    pool_recycle=280,     # recycle before Supabase pooler's 300s idle timeout
)

if _is_sqlite:
    # Enable WAL mode for concurrent reads during writes
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # Supabase free tier enforces a short statement_timeout — disable it per
    # connection so bulk ingestion isn't cancelled mid-insert.
    @event.listens_for(engine, "connect")
    def set_pg_timeouts(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("SET statement_timeout = 0")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
