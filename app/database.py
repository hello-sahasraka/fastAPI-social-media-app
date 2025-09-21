# database.py

from app.config import config
import sqlalchemy
import databases

metadata = sqlalchemy.MetaData()

# Example tables
post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String, nullable=False),
)

comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id")),
)

# If SQLite async, use a sync URL for table creation
sync_url = config.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

engine = sqlalchemy.create_engine(
    sync_url,
    connect_args={"check_same_thread": False} if sync_url.startswith("sqlite") else {},
)

# Create tables synchronously
metadata.create_all(engine)

# Async database instance
database = databases.Database(config.DATABASE_URL)
