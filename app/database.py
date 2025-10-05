from app.config import config
import sqlalchemy
import databases

metadata = sqlalchemy.MetaData()

user_table = sqlalchemy.Table(
    "user",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, autoincrement=True, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("confirmed", sqlalchemy.Boolean, default=False),
    sqlalchemy.Column("image_url", sqlalchemy.String),
)

post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("user.id")),
)

comments_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id")),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("user.id")),
)

likes_table = sqlalchemy.Table(
    "likes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id")),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("user.id")),
)

# If SQLite async, use a sync URL for table creation
sync_url = config.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

engine = sqlalchemy.create_engine(
    sync_url,
    connect_args={"check_same_thread": False} if sync_url.startswith("sqlite") else {},
)

# Create tables synchronously
metadata.drop_all(engine)
metadata.create_all(engine)

# Async database instance
database = databases.Database(config.DATABASE_URL)
