from fastapi import FastAPI
from app.routes.hackrx import router as hackrx_router
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="HackRx API", version="1.0.0")

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # Apply security globally to all endpoints
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"HTTPBearer": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# include router
app.include_router(hackrx_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

# root
@app.get("/")
async def root():
    return {"message": "HackRx API - POST /hackrx/run"}
