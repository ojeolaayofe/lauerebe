from fastapi import APIRouter, HTTPException, Depends
from auth import require_admin, db
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard-stats")
async def get_dashboard_stats(current_user: dict = Depends(require_admin)):
    try:
        total_properties = await db.properties.count_documents({})
        total_users = await db.users.count_documents({})
        total_investments = await db.investments.count_documents({})
        active_investments = await db.investments.count_documents({"status": "active"})
        total_transactions = await db.transactions.count_documents({})
        successful_transactions = await db.transactions.count_documents({"status": "success"})
        
        total_investment_amount = 0
        investments = await db.investments.find({}, {"_id": 0}).to_list(length=10000)
        for inv in investments:
            total_investment_amount += inv.get("amount", 0)
        
        return {
            "total_properties": total_properties,
            "total_users": total_users,
            "total_investments": total_investments,
            "active_investments": active_investments,
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "total_investment_amount": total_investment_amount
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_all_users(current_user: dict = Depends(require_admin)):
    try:
        users = await db.users.find({}, {"_id": 0}).to_list(length=1000)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/investments")
async def get_all_investments(current_user: dict = Depends(require_admin)):
    try:
        investments = await db.investments.find({}, {"_id": 0}).to_list(length=1000)
        
        for investment in investments:
            user = await db.users.find_one({"id": investment["user_id"]}, {"_id": 0, "email": 1, "phone": 1})
            property_doc = await db.properties.find_one({"id": investment["property_id"]}, {"_id": 0, "title": 1, "location": 1})
            investment["user"] = user
            investment["property"] = property_doc
        
        return investments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions")
async def get_all_transactions(current_user: dict = Depends(require_admin)):
    try:
        transactions = await db.transactions.find({}, {"_id": 0}).to_list(length=1000)
        
        for transaction in transactions:
            user = await db.users.find_one({"id": transaction["user_id"]}, {"_id": 0, "email": 1, "phone": 1})
            transaction["user"] = user
        
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
