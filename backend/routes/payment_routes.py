from fastapi import APIRouter, HTTPException, Depends, Request
from models import PaymentInitializeRequest
from auth import get_current_user, db
import uuid
import httpx
import hmac
import hashlib
import json
from datetime import datetime, timezone

router = APIRouter(prefix="/payments", tags=["payments"])

PAYSTACK_SECRET_KEY = "sk_test_demo_key"
PAYSTACK_BASE_URL = "https://api.paystack.co"

@router.post("/initialize")
async def initialize_payment(
    request: PaymentInitializeRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        reference = f"txn_{uuid.uuid4().hex[:12]}"
        amount_kobo = int(request.amount * 100)
        
        transaction_doc = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "investment_id": request.investment_id,
            "reference": reference,
            "amount": request.amount,
            "currency": request.currency,
            "status": "pending",
            "paystack_data": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "verified_at": None
        }
        
        await db.transactions.insert_one(transaction_doc)
        
        return {
            "authorization_url": f"https://checkout.paystack.com/mock/{reference}",
            "reference": reference,
            "access_code": f"access_{reference}",
            "message": "Payment initialized successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify/{reference}")
async def verify_payment(
    reference: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        transaction = await db.transactions.find_one({"reference": reference}, {"_id": 0})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction["user_id"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        await db.transactions.update_one(
            {"reference": reference},
            {
                "$set": {
                    "status": "success",
                    "verified_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if transaction.get("investment_id"):
            await db.investments.update_one(
                {"id": transaction["investment_id"]},
                {
                    "$set": {
                        "status": "active",
                        "initial_transaction_id": transaction["id"]
                    }
                }
            )
        
        return {
            "status": "success",
            "amount": transaction["amount"],
            "reference": reference,
            "message": "Payment verified successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def paystack_webhook(request: Request):
    try:
        signature = request.headers.get('x-paystack-signature')
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        body = await request.body()
        
        hash_object = hmac.new(
            PAYSTACK_SECRET_KEY.encode('utf-8'),
            body,
            hashlib.sha512
        )
        computed_hash = hash_object.hexdigest()
        
        if computed_hash != signature:
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        payload = json.loads(body)
        event = payload.get('event')
        data = payload.get('data', {})
        
        if event == 'charge.success':
            reference = data.get('reference')
            await db.transactions.update_one(
                {"reference": reference},
                {"$set": {"status": "success", "verified_at": datetime.now(timezone.utc).isoformat()}}
            )
        elif event == 'charge.failed':
            reference = data.get('reference')
            await db.transactions.update_one(
                {"reference": reference},
                {"$set": {"status": "failed"}}
            )
        
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
