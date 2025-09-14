"""
Main FastAPI application.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .database import init_db, close_db
from .kafka_client import start_kafka_consumer, stop_kafka_consumer
from .routes import kafka, nba, football

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting API")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Start Kafka consumer (commented out for local dev)
        await start_kafka_consumer()
        logger.info("Kafka consumer started")
        
        logger.info("API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to start API: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down API")
    
    try:
        # Stop Kafka consumer (commented out for local dev)
        await stop_kafka_consumer()
        
        # Close database connections
        await close_db()
        logger.info("Database connections closed")
        
        logger.info("API shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Error during API shutdown: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="Social Media Sentiment Analysis API",
    description="API for processing social media sentiment data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nba.router, prefix="/api/v1")
app.include_router(football.router, prefix="/api/v1")
app.include_router(kafka.router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", 
                 exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Social Media Sentiment Analysis API",
        "version": "1.0.0",
        "description": "API for processing social media sentiment data",
        "health_url": "/health"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2025-09-14T00:00:00Z",
        "version": "1.0.0"
    }


# Test endpoints
@app.get("/test/database")
async def test_database():
    """Test database connection."""
    try:
        from .database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1"))
            return {"status": "success", "message": f"Database connection working, {result.scalar()}"}
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.get("/test/kafka")
async def test_kafka():
    """Test Kafka connection."""
    try:
        from .kafka_client import kafka_client
        if kafka_client.is_connected:
            metadata = await kafka_client.get_topic_metadata()
            return {
                "status": "success", 
                "message": "Kafka connection working",
                "metadata": metadata
            }
        else:
            return {"status": "error", "message": "Kafka not connected"}
    except Exception as e:
        logger.error(f"Kafka test failed: {str(e)}")
        return {"status": "error", "message": str(e)}



if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
