import os
import re
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Dual-Mode Engine: High-concurrency SQLite WAL + Enterprise Postgres connection pooling
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Auto-resolve Supabase direct IPv6 address to IPv4 Pooler for cloud environments (Render lacks IPv6)
if ".supabase.co" in db_url and "pooler.supabase.com" not in db_url:
    match = re.match(r"^(postgresql\+psycopg2://)([^:]+):([^@]+)@db\.([a-z0-9]+)\.supabase\.co(?::\d+)?(/.*)?$", db_url)
    if match:
        prefix, user, pwd, ref, path = match.groups()
        pooler_user = f"{user}.{ref}" if "." not in user else user
        db_url = f"{prefix}{pooler_user}:{pwd}@aws-0-ap-south-1.pooler.supabase.com:5432{path or '/postgres'}"
        print(f"[DB INIT] Auto-translated Supabase direct IPv6 URL to IPv4 Pooler: aws-0-ap-south-1.pooler.supabase.com:5432")

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
    if "sslmode" not in db_url:
        engine_kwargs.setdefault("connect_args", {})["sslmode"] = "require"

try:
    if not is_sqlite:
        # Pre-flight check connection to catch network/credential issues before crashing the app
        test_eng = create_engine(db_url, **engine_kwargs)
        with test_eng.connect() as test_conn:
            test_conn.exec_driver_sql("SELECT 1;")
        engine = test_eng
        print(f"[DB INIT] Connected successfully to Cloud PostgreSQL (Supabase)!")
    else:
        engine = create_engine(db_url, **engine_kwargs)
except Exception as e:
    print(f"[DB INIT WARNING] Cloud PostgreSQL connection failed: {e}. Falling back to SQLite WAL mode to preserve zero-downtime uptime.")
    db_url = "sqlite:///./vyaparai.db"
    is_sqlite = True
    engine_kwargs = {"pool_pre_ping": True, "connect_args": {"check_same_thread": False, "timeout": 30.0}}
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
    else:
        with engine.begin() as conn:
            try:
                conn.exec_driver_sql("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS batch_id VARCHAR(64);")
                conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_transactions_batch_id ON transactions (batch_id);")
                conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_transactions_metrics_perf ON transactions (vendor_id, transaction_type, is_reversed, created_at);")
            except Exception as e:
                print(f"[DB INIT] PostgreSQL migration notice: {e}")
