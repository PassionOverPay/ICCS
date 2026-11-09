from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, communities, proposals, dashboard
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CommonGround Lite API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(communities.router, prefix="/api", tags=["communities"])
app.include_router(proposals.router, prefix="/api", tags=["proposals"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

