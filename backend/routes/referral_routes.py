from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from auth import get_current_user, db

router = APIRouter(prefix="/referrals", tags=["referrals"])

class ReferralCode(BaseModel):
    code: str
    user_id: str
    commission_rate: float = 5.0  # 5% default
    total_referrals: int = 0
    total_commission_earned: float = 0
    active: bool = True

@router.get("/my-referral-code")
async def get_my_referral_code(current_user: dict = Depends(get_current_user)):
    try:
        referral = await db.referrals.find_one({"user_id": current_user["id"]}, {"_id": 0})
        
        if not referral:
            # Generate new referral code
            code = f"REF{current_user['id'][:8].upper()}"
            referral = {
                "id": str(uuid.uuid4()),
                "code": code,
                "user_id": current_user["id"],
                "commission_rate": 5.0,
                "total_referrals": 0,
                "total_commission_earned": 0,
                "active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.referrals.insert_one(referral)
        
        # Get referred users
        referred_users = await db.users.find(
            {"referred_by": referral["code"]},
            {"_id": 0, "email": 1, "created_at": 1}
        ).to_list(length=100)
        
        referral["referred_users"] = referred_users
        return referral
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-referral-code/{code}")
async def apply_referral_code(code: str, current_user: dict = Depends(get_current_user)):
    try:
        # Check if user already has a referrer
        if current_user.get("referred_by"):
            raise HTTPException(status_code=400, detail="You already have a referrer")
        
        # Find referral code
        referral = await db.referrals.find_one({"code": code}, {"_id": 0})
        if not referral:
            raise HTTPException(status_code=404, detail="Invalid referral code")
        
        if referral["user_id"] == current_user["id"]:
            raise HTTPException(status_code=400, detail="Cannot use your own referral code")
        
        # Update user with referral
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"referred_by": code}}
        )
        
        # Update referral stats
        await db.referrals.update_one(
            {"code": code},
            {"$inc": {"total_referrals": 1}}
        )
        
        return {"message": "Referral code applied successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-commissions")
async def get_my_commissions(current_user: dict = Depends(get_current_user)):
    try:
        referral = await db.referrals.find_one({"user_id": current_user["id"]}, {"_id": 0})
        if not referral:
            return {"commissions": [], "total_earned": 0}
        
        # Get commission records
        commissions = await db.referral_commissions.find(
            {"referrer_id": current_user["id"]},
            {"_id": 0}
        ).to_list(length=100)
        
        return {
            "commissions": commissions,
            "total_earned": referral.get("total_commission_earned", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))