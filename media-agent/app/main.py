from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Media Analyst Agent",
    description="Agente de IA para análise de canais de mídia",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}