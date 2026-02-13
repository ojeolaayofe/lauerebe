from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from models import SendOTPRequest, VerifyOTPRequest, LoginRequest, AuthResponse, UserCreate, User
from auth import create_access_token, db
import random
import string
from datetime import datetime, timedelta, timezone
import uuid

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

def generate_otp_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

@router.post("/send-email-otp")
async def send_email_otp(request: SendOTPRequest):
    try:
        code = generate_otp_code()
        otp_doc = {
            "id": str(uuid.uuid4()),
            "contact": request.contact,
            "code": code,
            "type": "email",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
            "verified": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.otp_verifications.insert_one(otp_doc)
        
        return {"message": f"OTP sent to {request.contact}", "otp_for_testing": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-email-otp")
async def verify_email_otp(request: VerifyOTPRequest):
    try:
        otp_doc = await db.otp_verifications.find_one({
            "contact": request.contact,
            "code": request.code,
            "type": request.type,
            "verified": False
        }, {"_id": 0})
        
        if not otp_doc:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        expires_at = datetime.fromisoformat(otp_doc["expires_at"])
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="OTP has expired")
        
        await db.otp_verifications.update_one(
            {"id": otp_doc["id"]},
            {"$set": {"verified": True}}
        )
        
        user = await db.users.find_one({"email": request.contact}, {"_id": 0})
        if not user:
            user_doc = {
                "id": str(uuid.uuid4()),
                "email": request.contact,
                "phone": None,
                "first_name": None,
                "last_name": None,
                "role": "buyer",
                "email_verified": True,
                "whatsapp_verified": False,
                "favorites": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": None
            }
            await db.users.insert_one(user_doc)
            user = await db.users.find_one({"id": user_doc["id"]}, {"_id": 0})
        else:
            await db.users.update_one(
                {"email": request.contact},
                {"$set": {"email_verified": True}}
            )
            user = await db.users.find_one({"email": request.contact}, {"_id": 0})
        
        access_token = create_access_token(data={"sub": user["id"]})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-whatsapp-otp")
async def send_whatsapp_otp(request: SendOTPRequest):
    try:
        code = generate_otp_code()
        otp_doc = {
            "id": str(uuid.uuid4()),
            "contact": request.contact,
            "code": code,
            "type": "whatsapp",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
            "verified": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.otp_verifications.insert_one(otp_doc)
        
        return {"message": f"OTP sent via WhatsApp to {request.contact}", "otp_for_testing": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-whatsapp-otp")
async def verify_whatsapp_otp(request: VerifyOTPRequest):
    try:
        otp_doc = await db.otp_verifications.find_one({
            "contact": request.contact,
            "code": request.code,
            "type": request.type,
            "verified": False
        }, {"_id": 0})
        
        if not otp_doc:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        expires_at = datetime.fromisoformat(otp_doc["expires_at"])
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="OTP has expired")
        
        await db.otp_verifications.update_one(
            {"id": otp_doc["id"]},
            {"$set": {"verified": True}}
        )
        
        user = await db.users.find_one({"phone": request.contact}, {"_id": 0})
        if not user:
            user_doc = {
                "id": str(uuid.uuid4()),
                "email": None,
                "phone": request.contact,
                "first_name": None,
                "last_name": None,
                "role": "buyer",
                "email_verified": False,
                "whatsapp_verified": True,
                "favorites": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": None
            }
            await db.users.insert_one(user_doc)
            user = await db.users.find_one({"id": user_doc["id"]}, {"_id": 0})
        else:
            await db.users.update_one(
                {"phone": request.contact},
                {"$set": {"whatsapp_verified": True}}
            )
            user = await db.users.find_one({"phone": request.contact}, {"_id": 0})
        
        access_token = create_access_token(data={"sub": user["id"]})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user_info(credentials = Depends(security)):
    from auth import get_current_user
    user = await get_current_user(credentials)
    return user
