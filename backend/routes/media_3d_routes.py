from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List
import base64
import uuid
from datetime import datetime, timezone
from auth import get_current_user, require_admin, db

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/upload-3d")
async def upload_3d_media(
    property_id: str,
    files: List[UploadFile] = File(...),
    media_type: str = "model",  # model, 360_video, 360_image
    current_user: dict = Depends(require_admin)
):
    try:
        property_doc = await db.properties.find_one({"id": property_id})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        
        uploaded_media = []
        for file in files:
            contents = await file.read()
            base64_content = base64.b64encode(contents).decode('utf-8')
            
            # Determine MIME type based on file extension
            file_ext = file.filename.split('.')[-1].lower()
            mime_types = {
                'glb': 'model/gltf-binary',
                'gltf': 'model/gltf+json',
                'obj': 'model/obj',
                'fbx': 'model/fbx',
                'mp4': 'video/mp4',
                'webm': 'video/webm',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png'
            }
            
            mime_type = mime_types.get(file_ext, 'application/octet-stream')
            
            media_doc = {
                "id": str(uuid.uuid4()),
                "property_id": property_id,
                "filename": file.filename,
                "media_type": media_type,
                "file_type": mime_type,
                "content": base64_content,
                "size": len(contents),
                "uploaded_by": current_user["id"],
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.media_3d.insert_one(media_doc)
            
            uploaded_media.append({
                "id": media_doc["id"],
                "filename": media_doc["filename"],
                "media_type": media_type,
                "size": media_doc["size"]
            })
        
        # Update property with 3D media references
        await db.properties.update_one(
            {"id": property_id},
            {"$push": {"media_3d": {"$each": [m["id"] for m in uploaded_media]}}}
        )
        
        return {"message": f"Uploaded {len(uploaded_media)} 3D media files", "media": uploaded_media}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/property/{property_id}")
async def get_property_3d_media(property_id: str):
    try:
        media_list = await db.media_3d.find(
            {"property_id": property_id},
            {"_id": 0, "content": 0}  # Exclude large content from list
        ).to_list(length=100)
        
        return media_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{media_id}")
async def download_3d_media(media_id: str):
    try:
        media = await db.media_3d.find_one({"id": media_id}, {"_id": 0})
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        return {
            "filename": media["filename"],
            "content": media["content"],
            "file_type": media["file_type"],
            "media_type": media["media_type"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{media_id}")
async def delete_3d_media(
    media_id: str,
    current_user: dict = Depends(require_admin)
):
    try:
        media = await db.media_3d.find_one({"id": media_id})
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        await db.media_3d.delete_one({"id": media_id})
        
        # Remove reference from property
        await db.properties.update_one(
            {"id": media["property_id"]},
            {"$pull": {"media_3d": media_id}}
        )
        
        return {"message": "3D media deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))