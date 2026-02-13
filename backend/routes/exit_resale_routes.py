from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from auth import get_current_user, db

router = APIRouter(prefix="/exit-resale", tags=["exit-resale"])

class ExitRequestCreate(BaseModel):
    investment_id: str
    asking_price: float
    reason: Optional[str] = None
    urgent: bool = False

class ExitRequest(BaseModel):
    id: str
    investment_id: str
    user_id: str
    asking_price: float
    original_investment: float
    property_id: str
    reason: Optional[str]
    status: str  # pending, approved, rejected, completed
    urgent: bool
    created_at: str
    resolved_at: Optional[str] = None

@router.post("/request-exit")
async def request_exit(
    request: ExitRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get the investment
        investment = await db.investments.find_one({"id": request.investment_id}, {"_id": 0})
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
        
        if investment["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not your investment")
        
        if investment["status"] != "active":
            raise HTTPException(status_code=400, detail="Investment must be active to exit")
        
        # Create exit request
        exit_request = {
            "id": str(uuid.uuid4()),
            "investment_id": request.investment_id,
            "user_id": current_user["id"],
            "asking_price": request.asking_price,
            "original_investment": investment["amount"],
            "property_id": investment["property_id"],
            "reason": request.reason,
            "status": "pending",
            "urgent": request.urgent,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None
        }
        
        await db.exit_requests.insert_one(exit_request)
        
        return await db.exit_requests.find_one({"id": exit_request["id"]}, {"_id": 0})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-exit-requests")
async def get_my_exit_requests(
    current_user: dict = Depends(get_current_user)
):
    try:
        requests = await db.exit_requests.find(
            {"user_id": current_user["id"]},
            {"_id": 0}
        ).to_list(length=100)
        
        # Enrich with investment and property data
        for req in requests:
            investment = await db.investments.find_one({"id": req["investment_id"]}, {"_id": 0})
            property_doc = await db.properties.find_one({"id": req["property_id"]}, {"_id": 0})
            req["investment"] = investment
            req["property"] = property_doc
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketplace")
async def get_resale_marketplace():
    """Get all approved exit requests available for purchase"""
    try:
        approved_requests = await db.exit_requests.find(
            {"status": "approved"},
            {"_id": 0}
        ).to_list(length=100)
        
        # Enrich with property data
        for req in approved_requests:
            property_doc = await db.properties.find_one({"id": req["property_id"]}, {"_id": 0})
            investment = await db.investments.find_one({"id": req["investment_id"]}, {"_id": 0})
            req["property"] = property_doc
            req["investment"] = investment
        
        return approved_requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/purchase/{exit_request_id}")
async def purchase_resale(
    exit_request_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        exit_request = await db.exit_requests.find_one({"id": exit_request_id}, {"_id": 0})
        if not exit_request:
            raise HTTPException(status_code=404, detail="Exit request not found")
        
        if exit_request["status"] != "approved":
            raise HTTPException(status_code=400, detail="This investment is not available for purchase")
        
        # Get the investment
        investment = await db.investments.find_one({"id": exit_request["investment_id"]}, {"_id": 0})
        
        # Create new investment for buyer
        new_investment = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "property_id": investment["property_id"],
            "amount": exit_request["asking_price"],
            "currency": investment["currency"],
            "instalment_plan": None,
            "status": "active",
            "documents": [],
            "initial_transaction_id": None,
            "acquired_from_resale": True,
            "original_investment_id": investment["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        }
        
        # Update original investment
        await db.investments.update_one(
            {"id": investment["id"]},
            {"$set": {
                "status": "exited",
                "exit_date": datetime.now(timezone.utc).isoformat(),
                "exit_price": exit_request["asking_price"]
            }}
        )
        
        # Mark exit request as completed
        await db.exit_requests.update_one(
            {"id": exit_request_id},
            {"$set": {
                "status": "completed",
                "buyer_id": current_user["id"],
                "resolved_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Insert new investment
        await db.investments.insert_one(new_investment)
        
        return {
            "message": "Purchase successful",
            "new_investment": await db.investments.find_one({"id": new_investment["id"]}, {"_id": 0})
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/review/{exit_request_id}")
async def review_exit_request(
    exit_request_id: str,
    status: str,  # approved, rejected
    admin_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    from auth import require_admin
    await require_admin(current_user)
    
    try:
        if status not in ["approved", "rejected"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        await db.exit_requests.update_one(
            {"id": exit_request_id},
            {"$set": {
                "status": status,
                "admin_notes": admin_notes,
                "reviewed_by": current_user["id"],
                "resolved_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {"message": f"Exit request {status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/pending")
async def get_pending_exit_requests(current_user: dict = Depends(get_current_user)):
    from auth import require_admin
    await require_admin(current_user)
    
    try:
        requests = await db.exit_requests.find(
            {"status": "pending"},
            {"_id": 0}
        ).sort("urgent", -1).to_list(length=100)
        
        for req in requests:
            user = await db.users.find_one({"id": req["user_id"]}, {"_id": 0, "email": 1, "phone": 1})
            investment = await db.investments.find_one({"id": req["investment_id"]}, {"_id": 0})
            property_doc = await db.properties.find_one({"id": req["property_id"]}, {"_id": 0})
            req["user"] = user
            req["investment"] = investment
            req["property"] = property_doc
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))