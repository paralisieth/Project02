from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import vm_router, auth_router
from app.core.config import settings

app = FastAPI(
    title="Cyber Training Platform API",
    description="Backend API for managing VM access and lab environments",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(vm_router.router, prefix="/api/vms", tags=["Virtual Machines"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
