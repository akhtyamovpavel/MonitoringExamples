from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

import random

import asyncio
app = FastAPI()

Instrumentator().instrument(app).expose(app)


@app.get('/{id}')
async def get_id(id: int):
    await asyncio.sleep(random.random())
    return id
