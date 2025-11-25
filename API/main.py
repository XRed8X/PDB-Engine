"""
Main FastAPI application for PDB Engine API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import execute_command
from core.settings import settings
from router.protein_design import router as protein_router

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
