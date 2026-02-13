from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List
import base64
import uuid
from datetime import datetime, timezone
from auth import get_current_user, db

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    investment_id: str,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Verify investment ownership or admin
        investment = await db.investments.find_one({"id": investment_id})
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
        
        if investment["user_id"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        uploaded_docs = []
        for file in files:
            contents = await file.read()
            base64_content = base64.b64encode(contents).decode('utf-8')
            
            doc = {
                "id": str(uuid.uuid4()),
                "investment_id": investment_id,
                "filename": file.filename,
                "file_type": file.content_type,
                "content": base64_content,
                "size": len(contents),
                "uploaded_by": current_user["id"],
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.documents.insert_one(doc)
            uploaded_docs.append({
                "id": doc["id"],
                "filename": doc["filename"],
                "size": doc["size"]
            })
        
        # Update investment documents list
        await db.investments.update_one(
            {"id": investment_id},
            {"$push": {"documents": {"$each": [d["id"] for d in uploaded_docs]}}}
        )
        
        return {"message": f"Uploaded {len(uploaded_docs)} documents", "documents": uploaded_docs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/investment/{investment_id}")
async def get_investment_documents(
    investment_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        investment = await db.investments.find_one({"id": investment_id})
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
        
        if investment["user_id"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        documents = await db.documents.find(
            {"investment_id": investment_id},
            {"_id": 0, "content": 0}  # Exclude large base64 content from list
        ).to_list(length=100)
        
        return documents
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{document_id}")
async def download_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        doc = await db.documents.find_one({"id": document_id}, {"_id": 0})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Verify access
        investment = await db.investments.find_one({"id": doc["investment_id"]})
        if investment["user_id"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "filename": doc["filename"],
            "content": doc["content"],
            "file_type": doc["file_type"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        doc = await db.documents.find_one({"id": document_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if doc["uploaded_by"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        await db.documents.delete_one({"id": document_id})
        return {"message": "Document deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))