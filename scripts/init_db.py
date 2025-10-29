"""Initialize database tables."""
from app.database import init_db, engine, Base
from app.models import Review, Flag, DeletionRequest, User, ReviewerProfile, IPCluster
from loguru import logger


def main():
    """Initialize all database tables."""
    logger.info("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    logger.info("✓ Database tables created successfully")
    logger.info("✓ Review table initialized")
    logger.info("✓ Flag table initialized")
    logger.info("✓ DeletionRequest table initialized")
    logger.info("✓ User table initialized")
    logger.info("✓ ReviewerProfile table initialized")
    logger.info("✓ IPCluster table initialized")
    
    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    main()
