from fastapi import APIRouter, HTTPException
from models import WhatsAppInquiryRequest, WhatsAppBookingRequest
from auth import db
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

@router.post("/send-inquiry")
async def send_whatsapp_inquiry(request: WhatsAppInquiryRequest):
    try:
        property_doc = await db.properties.find_one({"id": request.property_id})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        
        inquiry_doc = {
            "id": str(uuid.uuid4()),
            "phone_number": request.phone_number,
            "property_id": request.property_id,
            "message": request.message,
            "type": "inquiry",
            "status": "sent",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.whatsapp_messages.insert_one(inquiry_doc)
        
        return {
            "message": "Inquiry sent successfully via WhatsApp",
            "phone_number": request.phone_number,
            "property_title": property_doc.get("title")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book-viewing")
async def book_viewing(request: WhatsAppBookingRequest):
    try:
        property_doc = await db.properties.find_one({"id": request.property_id})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        
        booking_doc = {
            "id": str(uuid.uuid4()),
            "phone_number": request.phone_number,
            "property_id": request.property_id,
            "viewing_date": request.viewing_date,
            "viewing_time": request.viewing_time,
            "type": "viewing",
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.whatsapp_messages.insert_one(booking_doc)
        
        message = f"Viewing booked for {property_doc.get('title')} on {request.viewing_date} at {request.viewing_time}. You will receive a WhatsApp confirmation shortly."
        
        return {
            "message": message,
            "booking_id": booking_doc["id"],
            "property_title": property_doc.get("title")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
