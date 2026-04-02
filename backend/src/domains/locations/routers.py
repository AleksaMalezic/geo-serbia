import hashlib
import json
import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from src.core.auth import get_current_admin, get_current_user
from src.domains.locations import schemas, services
from src.domains.users.models import User
from src.utils.pagination import get_pagination_params
from src.utils.response import paginated_response, success_response

router = APIRouter(prefix="/api/v1/locations", tags=["Locations"])

UPLOAD_DIR = "src/static/uploads/locations"


def _parse_hints(hints_raw: str | None) -> list[str] | None:
    if not hints_raw:
        return None
    try:
        value = json.loads(hints_raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Hints must be valid JSON array.") from exc

    if not isinstance(value, list):
        raise HTTPException(status_code=400, detail="Hints must be an array.")

    cleaned = []
    for item in value:
        if not isinstance(item, str):
            raise HTTPException(status_code=400, detail="Each hint must be a string.")
        text = item.strip()
        if text:
            cleaned.append(text)

    if len(cleaned) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 hints allowed.")
    return cleaned or None


@router.get("/")
async def get_locations(
    approved: bool | None = Query(True, description="Filter by status."),
    created_by: int | None = Query(None, description="Filter by user id."),
    search: str | None = Query(None, description="Filter by name."),
    pagination: dict = Depends(get_pagination_params),
):
    results = await services.filter_locations(approved, created_by, search)
    start = pagination["skip"]
    end = start + pagination["limit"]
    items = [schemas.LocationRead.model_validate(item).model_dump() for item in results[start:end]]
    return paginated_response(
        items=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=len(results),
        message="Items listed.",
    )


@router.get("/pending")
async def get_pending_locations(admin=Depends(get_current_admin)):
    locations = await services.get_pending_locations()
    serialized = [schemas.LocationRead.model_validate(item).model_dump() for item in locations]
    return success_response(serialized, message="Pending locations listed.")


@router.get("/{location_id}")
async def get_location_details(location_id: int):
    location = await services.get_location_details(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    serialized = schemas.LocationRead.model_validate(location).model_dump()
    return success_response(serialized, message="Location details retrieved.")


@router.post("/")
async def create_location(
    name: str = Form(...),
    description: str = Form(None),
    hints: str = Form(None),
    latitude: float = Form(...),
    longitude: float = Form(...),
    image: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    image_path = None
    max_file_size_mb = 5
    allowed_types = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
    }

    if image:
        if image.content_type not in allowed_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only jpg and png formats are supported.")

        content = await image.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > max_file_size_mb:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must not be bigger than {max_file_size_mb}MB",
            )

        ext = allowed_types[image.content_type]
        safe_name = f"{hashlib.sha256(content).hexdigest()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(content)

        image_path = f"/static/uploads/locations/{safe_name}"

    data = {
        "name": name,
        "description": description,
        "hints": _parse_hints(hints),
        "latitude": latitude,
        "longitude": longitude,
        "image_url": image_path,
    }

    location = await services.create_location(data, current_user)
    serialized = schemas.LocationRead.model_validate(location).model_dump()
    return success_response(serialized, message="Location created.")


@router.post("/{location_id}/approve")
async def approve_location(location_id: int, admin: User = Depends(get_current_admin)):
    updated = await services.approve_location(location_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Location not found.")
    return success_response({}, message="Location approved.")


@router.post("/{location_id}/reject")
async def reject_location(location_id: int, admin: User = Depends(get_current_admin)):
    deleted = await services.delete_location(location_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Location not found.")
    return success_response({}, message="Location rejected and deleted.")


@router.delete("/{location_id}")
async def delete_location(location_id: int):
    deleted = await services.delete_location(location_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Location not found.")
    return success_response({}, message="Location deleted successfully.")
