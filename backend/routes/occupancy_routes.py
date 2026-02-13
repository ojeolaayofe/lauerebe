from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
from auth import get_current_user, require_admin, db

router = APIRouter(prefix="/occupancy", tags=["occupancy"])

class OccupancyUpdate(BaseModel):
    property_id: str
    total_units: int
    occupied_units: int
    notes: Optional[str] = None

@router.post("/update")
async def update_occupancy(
    update: OccupancyUpdate,
    current_user: dict = Depends(require_admin)
):
    try:
        property_doc = await db.properties.find_one({"id": update.property_id})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        
        occupancy_doc = {
            "id": str(uuid.uuid4()),
            "property_id": update.property_id,
            "total_units": update.total_units,
            "occupied_units": update.occupied_units,
            "available_units": update.total_units - update.occupied_units,
            "occupancy_rate": (update.occupied_units / update.total_units * 100) if update.total_units > 0 else 0,
            "notes": update.notes,
            "updated_by": current_user["id"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update or insert
        await db.occupancy.update_one(
            {"property_id": update.property_id},
            {"$set": occupancy_doc},
            upsert=True
        )
        
        return occupancy_doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/property/{property_id}")
async def get_property_occupancy(property_id: str):
    try:
        occupancy = await db.occupancy.find_one(
            {"property_id": property_id},
            {"_id": 0}
        )
        
        if not occupancy:
            return {"message": "No occupancy data available"}
        
        return occupancy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
async def get_all_occupancy(current_user: dict = Depends(require_admin)):
    try:
        occupancy_data = await db.occupancy.find({}, {"_id": 0}).to_list(length=100)
        
        # Enrich with property data
        for occ in occupancy_data:
            property_doc = await db.properties.find_one(
                {"id": occ["property_id"]},
                {"_id": 0, "title": 1, "location": 1}
            )
            occ["property"] = property_doc
        
        return occupancy_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))