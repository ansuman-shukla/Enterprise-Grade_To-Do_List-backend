import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .database import connect_to_mongo, close_mongo_connection
from .routes import tasks

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up the application...")
    await connect_to_mongo()
    #check all api keys are set
    if os.getenv("GEMINI_API_KEY"):
        logger.info("GEMINI_API_KEY is set. Gemini service will be available.")
    else:
        logger.warning("GEMINI_API_KEY is not set. Gemini service will not be available.")
    
    yield
    # Shutdown
    logger.info("Shutting down the application...")
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title="Enterprise To-Do List API",
    description="A modern to-do list API with natural language processing capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Enterprise To-Do List API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running successfully"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


