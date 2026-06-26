from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    """
    GET /health
    Used for readiness and liveness checks (e.g. on Google Cloud Run).
    """
    return {"status": "ok"}
