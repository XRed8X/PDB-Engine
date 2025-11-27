"""
Main FastAPI application for PDB Engine API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import execute_command
from core.settings import settings
from router.protein_design import router as protein_router
from services.docker_executor import DockerExecutor

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Execution-Time", "X-Job-Status"],  # Expose custom headers
)

# app.include_router(protein_router)
app.include_router(execute_command.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with Docker status."""
    health_status = {
        "status": "healthy",
        "version": settings.API_VERSION,
        "execution_mode": "docker" if settings.USE_DOCKER else "local"
    }
    
    if settings.USE_DOCKER:
        
        docker_available = DockerExecutor.check_docker_available()
        health_status["docker_available"] = docker_available
        health_status["docker_image"] = settings.DOCKER_IMAGE
        
        if not docker_available:
            health_status["status"] = "unhealthy"
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)