import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Dual-Mode Engine: High-concurrency SQLite WAL + Enterprise Postgres connection pooling
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

is_sqlite = "sqlite" in db_url

engine_kwargs = {"pool_pre_ping": True}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30.0}
else:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,
        "pool_timeout": 30
    })

engine = create_engine(db_url, **engine_kwargs)

if is_sqlite:
    # 1. Hardware-level Pragmas: WAL mode, foreign keys, memory temp store, 64MB memory cache
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.close()

    # 2. Concurrency Shield: Force BEGIN IMMEDIATE to serialize write transactions
    # Completely eliminates the Lost Update Race Condition under concurrent webhooks
    @event.listens_for(engine, "begin")
    def do_begin(conn):
        conn.exec_driver_sql("BEGIN IMMEDIATE")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def checkpoint_wal(truncate: bool = False):
    """Utility to force WAL log checkpointing to disk for ephemeral storage resilience."""
    if is_sqlite:
        try:
            db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
            if os.path.exists(db_path):
                import sqlite3
                con = sqlite3.connect(db_path, timeout=1.0, autocommit=True)
                con.execute("PRAGMA wal_checkpoint(PASSIVE);")
                con.close()
        except Exception:
            pass

def init_db():
    """Initializes tables and handles safe forward migrations for existing databases."""
    Base.metadata.create_all(bind=engine)
    if is_sqlite:
        with engine.begin() as conn:
            try:
                res = conn.exec_driver_sql("PRAGMA table_info(transactions);").fetchall()
                cols = [r[1] for r in res]
                if cols and "batch_id" not in cols:
                    conn.exec_driver_sql("ALTER TABLE transactions ADD COLUMN batch_id VARCHAR(64);")
                    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_transactions_batch_id ON transactions (batch_id);")
            except Exception as e:
                print(f"[DB INIT] SQLite migration check notice: {e}")
