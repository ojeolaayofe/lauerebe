from fastapi import APIRouter, HTTPException, Depends, Query
from models import PropertyCreate, PropertyUpdate, Property, PropertyFilter
from auth import get_current_user, require_admin, db
from datetime import datetime, timezone
import uuid
from typing import Optional, List

router = APIRouter(prefix="/properties", tags=["properties"])

@router.get("/", response_model=List[Property])
async def get_properties(
    property_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    rental_yield_min: Optional[float] = Query(None),
    availability: Optional[str] = Query(None),
    limit: int = Query(50, le=100)
):
    try:
        query = {}
        if property_type:
            query["property_type"] = property_type
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        if price_min is not None or price_max is not None:
            query["price"] = {}
            if price_min is not None:
                query["price"]["$gte"] = price_min
            if price_max is not None:
                query["price"]["$lte"] = price_max
        if rental_yield_min is not None:
            query["investment_details.rental_yield"] = {"$gte": rental_yield_min}
        if availability:
            query["availability"] = availability
        
        properties = await db.properties.find(query, {"_id": 0}).limit(limit).to_list(length=limit)
        return properties
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{property_id}", response_model=Property)
async def get_property(property_id: str):
    try:
        property_doc = await db.properties.find_one({"id": property_id}, {"_id": 0})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        return property_doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Property)
async def create_property(
    property_data: PropertyCreate,
    current_user: dict = Depends(require_admin)
):
    try:
        property_doc = property_data.model_dump()
        property_doc["id"] = str(uuid.uuid4())
        property_doc["created_by"] = current_user["id"]
        property_doc["created_at"] = datetime.now(timezone.utc).isoformat()
        property_doc["updated_at"] = None
        
        await db.properties.insert_one(property_doc)
        
        return await db.properties.find_one({"id": property_doc["id"]}, {"_id": 0})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{property_id}", response_model=Property)
async def update_property(
    property_id: str,
    property_data: PropertyUpdate,
    current_user: dict = Depends(require_admin)
):
    try:
        existing_property = await db.properties.find_one({"id": property_id})
        if not existing_property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        update_data = {k: v for k, v in property_data.model_dump(exclude_unset=True).items() if v is not None}
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            await db.properties.update_one(
                {"id": property_id},
                {"$set": update_data}
            )
        
        return await db.properties.find_one({"id": property_id}, {"_id": 0})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{property_id}")
async def delete_property(
    property_id: str,
    current_user: dict = Depends(require_admin)
):
    try:
        result = await db.properties.delete_one({"id": property_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Property not found")
        return {"message": "Property deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
