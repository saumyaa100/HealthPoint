
from app.main import app as fastapi_app
from fastapi_vercel import vercel_app

app = vercel_app(fastapi_app)
