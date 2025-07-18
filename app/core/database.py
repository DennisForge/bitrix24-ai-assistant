"""
Database Configuration and Management

This module handles database connection, session management, and initialization
for the Bitrix24 AI Assistant application.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Create declarative base for models
Base = declarative_base()

# Async engine and session maker
async_engine = None
AsyncSessionLocal = None

# Sync engine and session maker (for migrations and init)
sync_engine = None
SessionLocal = None


def create_engines():
    """Create database engines for async and sync operations."""
    global async_engine, AsyncSessionLocal, sync_engine, SessionLocal
    
    # Create async engine
    async_engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        poolclass=QueuePool,
        pool_pre_ping=True,
        pool_recycle=3600,  # 1 hour
    )
    
    # Create async session maker
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    # Create sync engine for migrations
    sync_engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        poolclass=QueuePool,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    
    # Create sync session maker
    SessionLocal = sessionmaker(
        bind=sync_engine,
        autocommit=False,
        autoflush=False,
    )


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    
    Yields:
        AsyncSession: Database session
        
    Usage:
        async with get_async_session() as session:
            # Use session here
            pass
    """
    if AsyncSessionLocal is None:
        create_engines()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session() -> Session:
    """
    Get a sync database session.
    
    Returns:
        Session: Database session
        
    Usage:
        with get_sync_session() as session:
            # Use session here
            pass
    """
    if SessionLocal is None:
        create_engines()
    
    return SessionLocal()


async def init_db() -> None:
    """
    Initialize the database.
    
    Creates all tables defined in the models.
    """
    logger.info("Initializing database...")
    
    try:
        if async_engine is None:
            create_engines()
        
        # Import all models to ensure they are registered
        from app.models import task, calendar, user  # noqa: F401
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """
    Close database connections.
    
    Should be called during application shutdown.
    """
    logger.info("Closing database connections...")
    
    try:
        if async_engine:
            await async_engine.dispose()
        
        if sync_engine:
            sync_engine.dispose()
        
        logger.info("Database connections closed successfully")
        
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise


async def check_db_health() -> bool:
    """
    Check database connectivity.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        async with get_async_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


class DatabaseManager:
    """
    Database manager class for handling database operations.
    
    This class provides methods for common database operations
    and session management.
    """
    
    def __init__(self):
        """Initialize the database manager."""
        self.logger = get_logger(self.__class__.__name__)
    
    async def create_tables(self) -> None:
        """Create all database tables."""
        self.logger.info("Creating database tables...")
        
        try:
            if async_engine is None:
                create_engines()
            
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self.logger.info("Database tables created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create database tables: {e}")
            raise
    
    async def drop_tables(self) -> None:
        """Drop all database tables."""
        self.logger.warning("Dropping all database tables...")
        
        try:
            if async_engine is None:
                create_engines()
            
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            
            self.logger.info("Database tables dropped successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to drop database tables: {e}")
            raise
    
    async def reset_database(self) -> None:
        """Reset the database by dropping and recreating all tables."""
        self.logger.warning("Resetting database...")
        
        await self.drop_tables()
        await self.create_tables()
        
        self.logger.info("Database reset completed")


# Global database manager instance
db_manager = DatabaseManager()


# Dependency for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with get_async_session() as session:
        yield session
