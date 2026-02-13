from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user, db

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/my-notifications")
async def get_my_notifications(current_user: dict = Depends(get_current_user)):
    try:
        notifications = await db.notifications.find(
            {"user_id": current_user["id"]},
            {"_id": 0}
        ).sort("created_at", -1).to_list(length=50)
        
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/mark-read/{notification_id}")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        await db.notifications.update_one(
            {"id": notification_id, "user_id": current_user["id"]},
            {"$set": {"read": True}}
        )
        return {"message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/mark-all-read")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    try:
        await db.notifications.update_many(
            {"user_id": current_user["id"], "read": False},
            {"$set": {"read": True}}
        )
        return {"message": "All notifications marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    try:
        count = await db.notifications.count_documents(
            {"user_id": current_user["id"], "read": False}
        )
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))