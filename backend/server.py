from fastapi import FastAPI, APIRouter
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Real Estate Investment Platform API")

# Middleware to ensure HTTPS in redirects
class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get("location")
            if location and location.startswith("http://"):
                response.headers["location"] = location.replace("http://", "https://", 1)
        return response

app.add_middleware(HTTPSRedirectMiddleware)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Import route modules
from routes import (auth_routes, property_routes, ai_routes, investment_routes, payment_routes, 
                    whatsapp_routes, user_routes, admin_routes, upload_routes, exit_resale_routes, 
                    supplier_routes, referral_routes, appointment_routes, document_routes, 
                    materials_routes, occupancy_routes, notification_routes, social_routes,
                    media_3d_routes, report_routes)

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "Real Estate Investment Platform API", "version": "1.0.0"}

# Include all routers
api_router.include_router(auth_routes.router)
api_router.include_router(property_routes.router)
api_router.include_router(ai_routes.router)
api_router.include_router(investment_routes.router)
api_router.include_router(payment_routes.router)
api_router.include_router(whatsapp_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(admin_routes.router)
api_router.include_router(upload_routes.router)
api_router.include_router(exit_resale_routes.router)
api_router.include_router(supplier_routes.router)
api_router.include_router(referral_routes.router)
api_router.include_router(appointment_routes.router)
api_router.include_router(document_routes.router)
api_router.include_router(materials_routes.router)
api_router.include_router(occupancy_routes.router)
api_router.include_router(notification_routes.router)
api_router.include_router(social_routes.router)
api_router.include_router(media_3d_routes.router)
api_router.include_router(report_routes.router)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()