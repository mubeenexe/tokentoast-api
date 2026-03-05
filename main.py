from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: connect redis, run checks
    yield
    # shutdown: close connections cleanly

app = FastAPI(lifespan=lifespan)