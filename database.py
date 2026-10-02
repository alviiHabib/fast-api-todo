from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Connection URL format:
# dialect+driver://username:password@host:port/database_name
DATABASE_URL = "postgresql://postgres:it19004@localhost:5432/todo_fastAPI"

# 2. Engine: The core interface to the database.
# It holds the Connection Pool (reusable open TCP connections) 
# and the SQL Dialect (translates generic commands to PostgreSQL-specific SQL).
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Keeps up to 10 connections open in memory
    max_overflow=20,     # Spawns up to 20 temporary extra connections during load spikes
    echo=True            # Logs every generated SQL statement to the terminal (great for debugging)
)

# 3. SessionMaker: A factory that manufactures new Session objects.
# autocommit=False ensures transactions are safe and explicit.
# autoflush=False prevents premature syncing of state before commit.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 4. Declarative Base: A catalog where all table mappings register themselves.
Base = declarative_base()

# 5. Database Dependency for FastAPI
def get_db():
    """
    Creates an isolated database session per HTTP request,
    then automatically closes it when the request is done.
    """
    db = SessionLocal()
    try:
        yield db  # Injects the session into the FastAPI route handler
    finally:
        db.close()  # Guarantees connection return to pool, avoiding memory leaks