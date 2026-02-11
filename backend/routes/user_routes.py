from fastapi import APIRouter, HTTPException, Depends
from models import UserUpdate
from auth import get_current_user, db
from datetime import datetime, timezone

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/favorites")
async def get_favorites(current_user: dict = Depends(get_current_user)):
    try:
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        favorite_ids = user.get("favorites", [])
        
        if not favorite_ids:
            return []
        
        properties = await db.properties.find(
            {"id": {"$in": favorite_ids}},
            {"_id": 0}
        ).to_list(length=100)
        
        return properties
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/favorites/{property_id}")
async def add_to_favorites(
    property_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        property_doc = await db.properties.find_one({"id": property_id})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$addToSet": {"favorites": property_id}}
        )
        
        return {"message": "Property added to favorites"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/favorites/{property_id}")
async def remove_from_favorites(
    property_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$pull": {"favorites": property_id}}
        )
        
        return {"message": "Property removed from favorites"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile")
async def update_profile(
    profile_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        update_data = {k: v for k, v in profile_data.model_dump(exclude_unset=True).items() if v is not None}
        
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            await db.users.update_one(
                {"id": current_user["id"]},
                {"$set": update_data}
            )
        
        return await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
