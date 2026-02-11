from fastapi import APIRouter, HTTPException, Depends
from models import InvestmentCreate, Investment, APYCalculatorRequest, InstalmentCalculatorRequest, InstalmentPlan
from auth import get_current_user, db
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/investments", tags=["investments"])

@router.post("/calculate-apy")
async def calculate_apy(request: APYCalculatorRequest):
    try:
        principal = request.principal_amount
        rate = request.apy_rate / 100
        years = request.duration_years
        
        compound_frequency = 12
        total_amount = principal * ((1 + rate / compound_frequency) ** (compound_frequency * years))
        total_returns = total_amount - principal
        monthly_income = (total_returns / years) / 12
        
        return {
            "principal_amount": principal,
            "apy_rate": request.apy_rate,
            "duration_years": years,
            "total_amount": round(total_amount, 2),
            "total_returns": round(total_returns, 2),
            "monthly_passive_income": round(monthly_income, 2),
            "roi_percentage": round((total_returns / principal) * 100, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-instalment")
async def calculate_instalment(request: InstalmentCalculatorRequest):
    try:
        total_amount = request.total_amount
        down_payment = total_amount * (request.down_payment_percentage / 100)
        remaining_amount = total_amount - down_payment
        
        months = request.duration_months
        monthly_rate = request.interest_rate / 100 / 12
        
        if monthly_rate > 0:
            monthly_payment = remaining_amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
        else:
            monthly_payment = remaining_amount / months
        
        total_payment = down_payment + (monthly_payment * months)
        total_interest = total_payment - total_amount
        
        return {
            "total_amount": total_amount,
            "down_payment": round(down_payment, 2),
            "monthly_payment": round(monthly_payment, 2),
            "duration_months": months,
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "interest_rate": request.interest_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Investment)
async def create_investment(
    investment_data: InvestmentCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        property_doc = await db.properties.find_one({"id": investment_data.property_id})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        
        instalment_plan = None
        if investment_data.use_instalment:
            if not investment_data.down_payment_percentage or not investment_data.duration_months:
                raise HTTPException(status_code=400, detail="Instalment details required")
            
            down_payment = investment_data.amount * (investment_data.down_payment_percentage / 100)
            remaining = investment_data.amount - down_payment
            monthly_payment = remaining / investment_data.duration_months
            
            instalment_plan = {
                "total_amount": investment_data.amount,
                "down_payment": down_payment,
                "monthly_payment": monthly_payment,
                "duration_months": investment_data.duration_months,
                "total_instalments": investment_data.duration_months
            }
        
        investment_doc = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "property_id": investment_data.property_id,
            "amount": investment_data.amount,
            "currency": investment_data.currency,
            "instalment_plan": instalment_plan,
            "status": "pending",
            "documents": [],
            "initial_transaction_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        }
        
        await db.investments.insert_one(investment_doc)
        
        return await db.investments.find_one({"id": investment_doc["id"]}, {"_id": 0})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-investments")
async def get_my_investments(current_user: dict = Depends(get_current_user)):
    try:
        investments = await db.investments.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(length=100)
        
        for investment in investments:
            property_doc = await db.properties.find_one({"id": investment["property_id"]}, {"_id": 0})
            investment["property"] = property_doc
        
        return investments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{investment_id}")
async def get_investment(
    investment_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        investment = await db.investments.find_one({"id": investment_id}, {"_id": 0})
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
        
        if investment["user_id"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        property_doc = await db.properties.find_one({"id": investment["property_id"]}, {"_id": 0})
        investment["property"] = property_doc
        
        return investment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
