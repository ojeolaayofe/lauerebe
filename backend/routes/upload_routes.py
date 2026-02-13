from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List
import base64
import uuid
from auth import require_admin
import os

router = APIRouter(prefix="/upload", tags=["upload"])

# Simple base64 image storage for MVP
@router.post("/images")
async def upload_images(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(require_admin)
):
    try:
        uploaded_images = []
        
        for file in files:
            # Read file content
            contents = await file.read()
            
            # Convert to base64
            base64_image = base64.b64encode(contents).decode('utf-8')
            
            # Get file extension
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
            
            # Create data URL
            mime_type = f"image/{file_extension}"
            if file_extension == 'jpg':
                mime_type = "image/jpeg"
            
            data_url = f"data:{mime_type};base64,{base64_image}"
            
            uploaded_images.append({
                "url": data_url,
                "filename": file.filename,
                "size": len(contents)
            })
        
        return {
            "message": f"Successfully uploaded {len(uploaded_images)} images",
            "images": uploaded_images
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.delete("/images")
async def delete_image(
    image_url: str,
    current_user: dict = Depends(require_admin)
):
    # For base64 images, we just return success as they're stored in the property document
    return {"message": "Image reference deleted"}