from fastapi import APIRouter, Depends, HTTPException
from app.models.hackrx import HackRxRequest, HackRxResponse
from app.utils.auth import validate_bearer
from app.services.qa_pipeline import answer_questions_from_document
from app.utils.logger import get_logger
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
import asyncio

logger = get_logger(__name__)
router = APIRouter(prefix="/hackrx", tags=["hackrx"])

@router.post("/run", response_model=HackRxResponse)
async def run_hackrx(payload: HackRxRequest, _auth: bool = Depends(validate_bearer)):
    """
    Main entrypoint for /hackrx/run
    """
    try:
        # The heavy lifting is synchronous in services; run in threadpool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        answers = await loop.run_in_executor(None, answer_questions_from_document, payload.documents, payload.questions)
        return HackRxResponse(answers=answers)
    except Exception as e:
        logger.exception("Error processing /hackrx/run")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
