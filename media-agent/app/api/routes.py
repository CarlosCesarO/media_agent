from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.agent.media_agent import run_agent
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest) -> QueryResponse:
    try:
        answer = await run_agent(request.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels")
async def list_channels():
    return {
        "channels": ["Search", "Organic", "Facebook", "Email", "Display"]
    }