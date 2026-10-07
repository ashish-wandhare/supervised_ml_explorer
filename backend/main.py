from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine, Base
from routers import datasets, training, results, analysis

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Supervised Learning Explorer API",
    description="A professional ML platform to train, compare, and analyse supervised learning algorithms.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(training.router, prefix="/api/train", tags=["Training"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "app": "Supervised Learning Explorer",
        "version": "1.0.0",
        "docs": "/docs",
    }
