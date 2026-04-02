from pathlib import Path

from src.domains.locations.models import Location
from tortoise.expressions import Q
from src.domains.users.models import User

UPLOAD_URL_PREFIX = "/static/uploads/locations/"
UPLOAD_DIR = Path("src/static/uploads/locations")


async def get_all_locations():
    return await Location.all()

async def get_location_details(location_id: int):
    return await Location.filter(id=location_id).first()

async def create_location(data: dict, current_user: User):
    payload = {**data}
    payload["created_by_id"] = current_user.id
    payload["is_approved"] = bool(current_user.is_admin)
    return await Location.create(**payload)

async def delete_location(location_id: int):
    location = await Location.filter(id=location_id).first()
    if location:
        image_url = location.image_url
        await location.delete()

        # Remove file only if no other location references the same image.
        if image_url:
            in_use = await Location.filter(image_url=image_url).exists()
            if not in_use and image_url.startswith(UPLOAD_URL_PREFIX):
                filename = image_url.replace(UPLOAD_URL_PREFIX, "", 1)
                file_path = UPLOAD_DIR / filename
                if file_path.exists() and file_path.is_file():
                    file_path.unlink()
        return True
    return False

async def approve_location(location_id: int):
    location = await Location.filter(id=location_id).first()
    if not location:
        return False
    location.is_approved = True
    await location.save()
    return True

async def get_pending_locations():
    return await Location.filter(is_approved=False).all()


async def filter_locations(
    approved: bool | None, 
    created_by: int | None, 
    search: str | None
):
    query = Location.all()
    
    if approved is not None:
        query = query.filter(is_approved=approved)
    if created_by is not None:
        query = query.filter(created_by_id=created_by)
    if search:
        query = query.filter(Q(name__icontains=search) | Q(description__icontains=search))
        
    return await query
