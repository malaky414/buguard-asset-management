from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import create_tables
from app.api.routes import assets, analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup
    await create_tables()
    yield
    # Runs on shutdown (nothing needed for now)


app = FastAPI(
    title="Buguard Asset Management — AI Track",
    description="LangChain-powered Attack Surface Monitoring asset analysis",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(assets.router, prefix="/assets", tags=["Assets"])
app.include_router(analysis.router, prefix="/analyze", tags=["AI Analysis"])


@app.get("/health")
async def health():
    return {"status": "ok"}
