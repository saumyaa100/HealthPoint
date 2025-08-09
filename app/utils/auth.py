# from fastapi import Header, HTTPException, status, Depends
# from .logger import get_logger
# import app.config as cfg

# logger = get_logger(__name__)

# def validate_bearer(authorization: str = Header(None)):
#     """
#     Header: Authorization: Bearer <api_key>
#     """
#     if not authorization:
#         logger.warning("Missing Authorization header")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
#     try:
#         scheme, token = authorization.split()
#     except Exception:
#         logger.warning("Malformed Authorization header")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed Authorization header")
#     if scheme.lower() != "bearer" or token != cfg.API_KEY:
#         logger.warning("Invalid API key")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
#     return True


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .logger import get_logger
import app.config as cfg

logger = get_logger(__name__)

security = HTTPBearer()

def validate_bearer(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates Bearer token using FastAPI's HTTPBearer.
    """

    print("Received:", credentials.credentials, "Expected:", cfg.API_KEY)  # <-- Add this line

    if credentials is None:
        logger.warning("Missing Authorization header")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    if credentials.scheme.lower() != "bearer" or credentials.credentials != cfg.API_KEY:
        logger.warning("Invalid API key")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return True