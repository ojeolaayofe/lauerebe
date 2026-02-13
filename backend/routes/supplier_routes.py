from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from auth import get_current_user, require_admin, db

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

class SupplierOnboarding(BaseModel):
    business_name: str
    contact_person: str
    phone: str
    email: str
    service_category: str  # construction, plumbing, electrical, etc.
    years_experience: int
    portfolio_description: str
    equity_interest: bool = False

class WorkAssignment(BaseModel):
    property_id: str
    supplier_id: str
    work_description: str
    estimated_cost: float
    estimated_duration_days: int
    equity_percentage: Optional[float] = 0

@router.post("/onboard")
async def onboard_supplier(
    data: SupplierOnboarding,
    current_user: dict = Depends(get_current_user)
):
    try:
        supplier = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "business_name": data.business_name,
            "contact_person": data.contact_person,
            "phone": data.phone,
            "email": data.email,
            "service_category": data.service_category,
            "years_experience": data.years_experience,
            "portfolio_description": data.portfolio_description,
            "equity_interest": data.equity_interest,
            "status": "pending",  # pending, approved, rejected
            "rating": 0,
            "completed_projects": 0,
            "total_equity_earned": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.suppliers.insert_one(supplier)
        
        # Update user role
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"role": "supplier"}}
        )
        
        return {"message": "Supplier application submitted", "supplier": supplier}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-profile")
async def get_supplier_profile(current_user: dict = Depends(get_current_user)):
    try:
        supplier = await db.suppliers.find_one({"user_id": current_user["id"]}, {"_id": 0})
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier profile not found")
        return supplier
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-assignments")
async def get_my_assignments(current_user: dict = Depends(get_current_user)):
    try:
        supplier = await db.suppliers.find_one({"user_id": current_user["id"]}, {"_id": 0})
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier profile not found")
        
        assignments = await db.work_assignments.find(
            {"supplier_id": supplier["id"]},
            {"_id": 0}
        ).to_list(length=100)
        
        # Enrich with property data
        for assignment in assignments:
            property_doc = await db.properties.find_one({"id": assignment["property_id"]}, {"_id": 0})
            assignment["property"] = property_doc
        
        return assignments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/assign-work")
async def assign_work(
    assignment: WorkAssignment,
    current_user: dict = Depends(require_admin)
):
    try:
        work = {
            "id": str(uuid.uuid4()),
            "property_id": assignment.property_id,
            "supplier_id": assignment.supplier_id,
            "work_description": assignment.work_description,
            "estimated_cost": assignment.estimated_cost,
            "estimated_duration_days": assignment.estimated_duration_days,
            "equity_percentage": assignment.equity_percentage,
            "status": "assigned",  # assigned, in_progress, completed, cancelled
            "actual_cost": None,
            "completion_date": None,
            "assigned_by": current_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.work_assignments.insert_one(work)
        return {"message": "Work assigned successfully", "assignment": work}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-assignment/{assignment_id}")
async def update_assignment_status(
    assignment_id: str,
    status: str,
    actual_cost: Optional[float] = None,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        assignment = await db.work_assignments.find_one({"id": assignment_id})
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Check if user is the assigned supplier
        supplier = await db.suppliers.find_one({"user_id": current_user["id"]})
        if not supplier or supplier["id"] != assignment["supplier_id"]:
            if current_user.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Not authorized")
        
        update_data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if actual_cost:
            update_data["actual_cost"] = actual_cost
        if notes:
            update_data["notes"] = notes
        if status == "completed":
            update_data["completion_date"] = datetime.now(timezone.utc).isoformat()
            
            # Update supplier stats
            await db.suppliers.update_one(
                {"id": assignment["supplier_id"]},
                {
                    "$inc": {
                        "completed_projects": 1,
                        "total_equity_earned": assignment.get("equity_percentage", 0)
                    }
                }
            )
        
        await db.work_assignments.update_one(
            {"id": assignment_id},
            {"$set": update_data}
        )
        
        return {"message": "Assignment updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/all-suppliers")
async def get_all_suppliers(current_user: dict = Depends(require_admin)):
    try:
        suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(length=100)
        return suppliers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/approve-supplier/{supplier_id}")
async def approve_supplier(
    supplier_id: str,
    status: str,  # approved, rejected
    current_user: dict = Depends(require_admin)
):
    try:
        await db.suppliers.update_one(
            {"id": supplier_id},
            {"$set": {"status": status}}
        )
        return {"message": f"Supplier {status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))