from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from auth import get_current_user, db

router = APIRouter(prefix="/social", tags=["social"])

class SocialPost(BaseModel):
    content: str
    property_id: Optional[str] = None
    investment_id: Optional[str] = None
    images: Optional[List[str]] = []

@router.post("/post")
async def create_social_post(
    post: SocialPost,
    current_user: dict = Depends(get_current_user)
):
    try:
        post_doc = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "content": post.content,
            "property_id": post.property_id,
            "investment_id": post.investment_id,
            "images": post.images or [],
            "likes": [],
            "comments": [],
            "shares": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.social_posts.insert_one(post_doc)
        return post_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feed")
async def get_social_feed(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    try:
        posts = await db.social_posts.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        # Enrich with user and property data
        for post in posts:
            user = await db.users.find_one(
                {"id": post["user_id"]},
                {"_id": 0, "email": 1, "first_name": 1, "last_name": 1}
            )
            post["user"] = user
            
            if post.get("property_id"):
                property_doc = await db.properties.find_one(
                    {"id": post["property_id"]},
                    {"_id": 0, "title": 1, "images": 1, "location": 1}
                )
                post["property"] = property_doc
        
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/like/{post_id}")
async def like_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        post = await db.social_posts.find_one({"id": post_id})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        likes = post.get("likes", [])
        if current_user["id"] in likes:
            # Unlike
            await db.social_posts.update_one(
                {"id": post_id},
                {"$pull": {"likes": current_user["id"]}}
            )
            return {"message": "Post unliked", "liked": False}
        else:
            # Like
            await db.social_posts.update_one(
                {"id": post_id},
                {"$addToSet": {"likes": current_user["id"]}}
            )
            return {"message": "Post liked", "liked": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comment/{post_id}")
async def add_comment(
    post_id: str,
    comment_text: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        comment = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "text": comment_text,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.social_posts.update_one(
            {"id": post_id},
            {"$push": {"comments": comment}}
        )
        
        return {"message": "Comment added", "comment": comment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/share/{post_id}")
async def share_post(
    post_id: str,
    platform: str,  # facebook, twitter, whatsapp, linkedin
    current_user: dict = Depends(get_current_user)
):
    try:
        post = await db.social_posts.find_one({"id": post_id})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Increment share count
        await db.social_posts.update_one(
            {"id": post_id},
            {"$inc": {"shares": 1}}
        )
        
        # Generate share URL
        base_url = "https://real-estate-pro-14.preview.emergentagent.com"
        
        if post.get("property_id"):
            share_url = f"{base_url}/properties/{post['property_id']}"
            property_doc = await db.properties.find_one({"id": post["property_id"]})
            share_text = f"Check out this investment opportunity: {property_doc.get('title')}"
        else:
            share_url = base_url
            share_text = post["content"]
        
        share_links = {
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={share_url}",
            "twitter": f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}",
            "whatsapp": f"https://wa.me/?text={share_text} {share_url}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={share_url}"
        }
        
        return {
            "message": "Share link generated",
            "share_url": share_links.get(platform, share_url),
            "platform": platform
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))