from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import engine, Base
from app.models.organization import Organization  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.project_member import ProjectMember  # noqa: F401
from app.models.activity_log import ActivityLog  # noqa: F401
from app.models.message import Message  # noqa: F401

from app.routers import (
    auth,
    users,
    projects,
    tasks,
    activity,
    ws,
    organization,
    messages,
    ml,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="TaskForge API",
    description="Org-Based Hierarchical Task Management",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)},
    )


app.include_router(auth.router)
app.include_router(organization.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(activity.router)
app.include_router(messages.router)
app.include_router(ws.router)
app.include_router(ml.router, prefix="/api/ml", tags=["ML"])


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ── Serve Frontend Static Files ──────────────────────────────────────
# Mount static files (JS, CSS, images)
if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

    # Catch-all for SPA routing (must be at the end)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Prevent shadowing API routes (though they should be matched first)
        if full_path.startswith("api") or full_path.startswith("ws"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
            
        index_path = os.path.join("dist", "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return JSONResponse(status_code=404, content={"detail": "Frontend build not found"})
else:
    @app.get("/")
    async def root():
        return {"message": "TaskForge API v2 is running", "docs": "/docs"}
