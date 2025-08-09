
from app.main import app  # reuse the FastAPI instance defined in app/main.py

# NOTE:
# For Vercel Python serverless runtime, expose a module-level variable named "app"
# that is an ASGI application. Avoid wrapping with Mangum unless targeting AWS Lambda.
# The previous "handler = Mangum(app)" triggered Vercel's runtime to treat the object
# as a BaseHTTPRequestHandler subclass, leading to issubclass() TypeError.
