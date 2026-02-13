from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
import uuid
from auth import get_current_user, db

router = APIRouter(prefix="/appointments", tags=["appointments"])

class AppointmentCreate(BaseModel):
    property_id: str
    appointment_date: str
    appointment_time: str
    visitor_name: str
    visitor_phone: str
    visitor_email: str
    notes: Optional[str] = None

@router.post("/book")
async def book_appointment(
    appointment: AppointmentCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        property_doc = await db.properties.find_one({"id": appointment.property_id})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        
        appointment_doc = {
            "id": str(uuid.uuid4()),
            "property_id": appointment.property_id,
            "user_id": current_user["id"],
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time,
            "visitor_name": appointment.visitor_name,
            "visitor_phone": appointment.visitor_phone,
            "visitor_email": appointment.visitor_email,
            "notes": appointment.notes,
            "status": "pending",  # pending, confirmed, cancelled, completed
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.appointments.insert_one(appointment_doc)
        
        # Create notification
        await create_notification(
            current_user["id"],
            f"Appointment booked for {property_doc.get('title')}",
            f"Your viewing is scheduled for {appointment.appointment_date} at {appointment.appointment_time}"
        )
        
        return {"message": "Appointment booked successfully", "appointment": appointment_doc}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-appointments")
async def get_my_appointments(current_user: dict = Depends(get_current_user)):
    try:
        appointments = await db.appointments.find(
            {"user_id": current_user["id"]},
            {"_id": 0}
        ).to_list(length=100)
        
        for apt in appointments:
            property_doc = await db.properties.find_one({"id": apt["property_id"]}, {"_id": 0})
            apt["property"] = property_doc
        
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{appointment_id}")
async def update_appointment(
    appointment_id: str,
    status: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        appointment = await db.appointments.find_one({"id": appointment_id})
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        await db.appointments.update_one(
            {"id": appointment_id},
            {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {"message": "Appointment updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def create_notification(user_id: str, title: str, message: str):
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "message": message,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)