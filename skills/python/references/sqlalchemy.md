# SQLAlchemy

SQLAlchemy 2.0 async patterns: engine/session setup, `Mapped`/`mapped_column`
models, relationships, 2.0-style `select()` queries, eager loading,
aggregations, CTEs, the repository pattern, and Alembic. Core conventions
live in `../SKILL.md`.

## Database setup (async)

`expire_on_commit=False` keeps loaded attributes available after commit in
async sessions:

```python
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Model patterns

### DeclarativeBase with Mapped / mapped_column

```python
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    posts: Mapped[list["Post"]] = relationship(
        back_populates="author", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
```

### Relationships

```python
from sqlalchemy import ForeignKey, Table, Column, Integer


class Post(TimestampMixin, Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Many-to-one
    author: Mapped["User"] = relationship(back_populates="posts")

    # Many-to-many
    tags: Mapped[list["Tag"]] = relationship(
        secondary="post_tags", back_populates="posts"
    )


# Association table for many-to-many
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    posts: Mapped[list["Post"]] = relationship(
        secondary="post_tags", back_populates="tags"
    )
```

### Enum and JSON fields

```python
import enum
from sqlalchemy import Enum, JSON
from sqlalchemy.dialects.postgresql import JSONB


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
```

## Query patterns (2.0 style)

Prefer `select()` over the legacy `Query` API — better type support and
consistency between sync and async:

```python
from sqlalchemy import select, func


# Get by ID
stmt = select(User).where(User.id == user_id)
result = await session.execute(stmt)
user = result.scalar_one_or_none()

# Filter with multiple conditions
stmt = select(User).where(User.is_active == True, User.role == UserRole.ADMIN)  # noqa: E712
result = await session.execute(stmt)
admins = result.scalars().all()

# Order and limit
stmt = select(User).order_by(User.created_at.desc()).limit(20).offset(0)

# Count
stmt = select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
result = await session.execute(stmt)
count = result.scalar()
```

### Eager loading (avoid N+1)

```python
from sqlalchemy.orm import selectinload, joinedload


# selectinload - separate SELECT IN, best for collections
stmt = select(User).options(selectinload(User.posts)).where(User.id == user_id)

# joinedload - LEFT JOIN, best for single related objects
stmt = select(Post).options(joinedload(Post.author)).where(Post.id == post_id)

# Nested eager loading
stmt = select(User).options(
    selectinload(User.posts).selectinload(Post.tags)
)
```

### Aggregations

```python
from sqlalchemy import case


# Group by with aggregation
stmt = (
    select(
        User.role,
        func.count(User.id).label("count"),
    )
    .group_by(User.role)
)

# Conditional aggregation
stmt = select(
    func.count(case((User.is_active == True, 1))).label("active_count"),  # noqa: E712
    func.count(case((User.is_active == False, 1))).label("inactive_count"),  # noqa: E712
)
```

### Subqueries and CTEs

```python
# Correlated subquery
subq = (
    select(func.count(Post.id))
    .where(Post.author_id == User.id)
    .correlate(User)
    .scalar_subquery()
)
stmt = select(User, subq.label("post_count")).order_by(subq.desc())

# Common Table Expression
active_users = (
    select(User.id, User.name)
    .where(User.is_active == True)  # noqa: E712
    .cte("active_users")
)
stmt = (
    select(active_users.c.name, func.count(Post.id))
    .join(Post, Post.author_id == active_users.c.id)
    .group_by(active_users.c.name)
)
```

## Repository pattern

A generic `BaseRepository[T]` centralizes data access; subclasses add
domain-specific queries:

```python
from typing import Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def get(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, obj: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.session.flush()
        return obj

    async def delete(self, obj: T) -> None:
        await self.session.delete(obj)
        await self.session.flush()


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_users(self) -> list[User]:
        stmt = (
            select(User)
            .where(User.is_active == True)  # noqa: E712
            .order_by(User.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
```

## Alembic setup

```bash
alembic init alembic                          # initialize
alembic revision --autogenerate -m "msg"     # generate migration
alembic upgrade head                          # apply
alembic downgrade -1                          # rollback one
alembic current                               # current version
alembic history                               # history
```

### alembic/env.py (async)

```python
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import Base
from app.config import settings

target_metadata = Base.metadata


def run_migrations_online() -> None:
    connectable = create_async_engine(settings.DATABASE_URL)

    async def do_run_migrations(connection):
        await connection.run_sync(do_run_migrations_sync)

    def do_run_migrations_sync(connection):
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    import asyncio
    asyncio.run(do_run_migrations(connectable))
```

## Performance tips

1. **Eager-load relationships** you'll access — `selectinload` for
   collections, `joinedload` for single objects
2. **Use `select()`**, not legacy `session.query()` — 2.0 style
3. **Avoid N+1** — eager load or join rather than accessing relationships in a
   loop
4. **`expire_on_commit=False`** in async sessions — avoids unexpected refreshes
5. **Batch inserts** — `session.add_all()` or `insert().values()`
6. **Connection pooling** — tune `pool_size` and `max_overflow`
7. **Index** frequently filtered columns — `index=True`

## Quick reference

| Pattern | Usage |
|---|---|
| `select(Model)` | Build a SELECT query |
| `session.execute(stmt)` | Execute the query |
| `result.scalars().all()` | List of objects |
| `result.scalar_one_or_none()` | Single object or `None` |
| `selectinload(Model.rel)` | Eager-load a collection |
| `joinedload(Model.rel)` | Eager-load a single object |
| `session.add(obj)` | Queue an insert |
| `session.flush()` | Write to DB without committing |
| `session.commit()` | Commit the transaction |

Adapted from [manikosto/claude-code-python-stack](https://github.com/manikosto/claude-code-python-stack).
