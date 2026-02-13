from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from auth import get_current_user, require_admin, db

router = APIRouter(prefix="/materials", tags=["materials"])

class MaterialItem(BaseModel):
    name: str
    quantity_needed: float
    unit: str  # kg, bags, pieces, etc.
    estimated_cost: float

class LabourCategory(BaseModel):
    category: str  # mason, plumber, electrician, etc.
    workers_needed: int
    days_needed: int
    cost_per_day: float

class MaterialsLabourPlan(BaseModel):
    property_id: str
    materials: List[MaterialItem]
    labour: List[LabourCategory]

@router.post("/plan")
async def create_materials_labour_plan(
    plan: MaterialsLabourPlan,
    current_user: dict = Depends(require_admin)
):
    try:
        # Calculate totals
        total_materials_cost = sum(item.quantity_needed * item.estimated_cost for item in plan.materials)
        total_labour_cost = sum(cat.workers_needed * cat.days_needed * cat.cost_per_day for cat in plan.labour)
        
        plan_doc = {
            "id": str(uuid.uuid4()),
            "property_id": plan.property_id,
            "materials": [m.dict() for m in plan.materials],
            "labour": [l.dict() for l in plan.labour],
            "total_materials_cost": total_materials_cost,
            "total_labour_cost": total_labour_cost,
            "total_cost": total_materials_cost + total_labour_cost,
            "materials_raised": 0,
            "labour_raised": 0,
            "status": "planning",  # planning, fundraising, in_progress, completed
            "created_by": current_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.materials_labour_plans.insert_one(plan_doc)
        return plan_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/property/{property_id}")
async def get_property_plan(property_id: str):
    try:
        plan = await db.materials_labour_plans.find_one(
            {"property_id": property_id},
            {"_id": 0}
        )
        
        if not plan:
            return {"message": "No plan found for this property"}
        
        # Calculate progress percentages
        materials_progress = (plan["materials_raised"] / plan["total_materials_cost"] * 100) if plan["total_materials_cost"] > 0 else 0
        labour_progress = (plan["labour_raised"] / plan["total_labour_cost"] * 100) if plan["total_labour_cost"] > 0 else 0
        
        plan["materials_progress"] = round(materials_progress, 2)
        plan["labour_progress"] = round(labour_progress, 2)
        plan["materials_remaining"] = plan["total_materials_cost"] - plan["materials_raised"]
        plan["labour_remaining"] = plan["total_labour_cost"] - plan["labour_raised"]
        
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contribute/{plan_id}")
async def contribute_to_plan(
    plan_id: str,
    materials_amount: float = 0,
    labour_amount: float = 0,
    current_user: dict = Depends(get_current_user)
):
    try:
        plan = await db.materials_labour_plans.find_one({"id": plan_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Record contribution
        contribution = {
            "id": str(uuid.uuid4()),
            "plan_id": plan_id,
            "user_id": current_user["id"],
            "materials_amount": materials_amount,
            "labour_amount": labour_amount,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.material_contributions.insert_one(contribution)
        
        # Update plan totals
        await db.materials_labour_plans.update_one(
            {"id": plan_id},
            {
                "$inc": {
                    "materials_raised": materials_amount,
                    "labour_raised": labour_amount
                }
            }
        )
        
        return {"message": "Contribution recorded", "contribution": contribution}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contributions/{plan_id}")
async def get_plan_contributions(plan_id: str):
    try:
        contributions = await db.material_contributions.find(
            {"plan_id": plan_id},
            {"_id": 0}
        ).to_list(length=100)
        
        # Enrich with user data
        for contrib in contributions:
            user = await db.users.find_one({"id": contrib["user_id"]}, {"_id": 0, "email": 1, "phone": 1})
            contrib["user"] = user
        
        return contributions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))