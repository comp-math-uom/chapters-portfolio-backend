from datetime import datetime
from fastapi import APIRouter, Depends

from auth.jwt_bearer import require_admin
from models.about_us import AboutUs
from schemas.about_us import AboutUsSchema, AboutUsUpdateSchema

router = APIRouter()


async def _get_or_seed() -> AboutUs:
    """Return the singleton AboutUs document, creating an empty one if missing."""
    doc = await AboutUs.find_one(AboutUs.key == "main")
    if doc is None:
        doc = AboutUs(key="main")
        await doc.insert()
    return doc


@router.get("", response_model=AboutUsSchema)
async def get_about_us():
    """Public read. Auto-seeds an empty document on first request."""
    return await _get_or_seed()


@router.put("", response_model=AboutUsSchema, dependencies=[Depends(require_admin)])
async def update_about_us(payload: AboutUsUpdateSchema):
    """Admin upsert. Partial update — only provided fields change."""
    doc = await _get_or_seed()
    update_data = payload.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await doc.update({"$set": update_data})
    return await AboutUs.get(doc.id)
