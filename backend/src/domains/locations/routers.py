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


def _detect_image_ext(content: bytes) -> str | None:
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    return None


@router.get("/")
async def get_locations(
    approved: bool | None = Query(True, description="Filter by status."),
    created_by: int | None = Query(None, description="Filter by user id."),
    search: str | None = Query(None, description="Filter by name."),
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
):
    if approved is not True and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required for non-approved locations.")

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


@router.get("/admin/all")
async def get_all_locations_for_admin(
    approved: bool | None = Query(None, description="Filter by status."),
    created_by: int | None = Query(None, description="Filter by user id."),
    search: str | None = Query(None, description="Filter by name."),
    pagination: dict = Depends(get_pagination_params),
    admin: User = Depends(get_current_admin),
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


@router.get("/{location_id}")
async def get_location_details(location_id: int, current_user: User = Depends(get_current_user)):
    location = await services.get_location_details(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    if not location.is_approved and not current_user.is_admin:
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

    if image:
        content = await image.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > max_file_size_mb:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must not be bigger than {max_file_size_mb}MB",
            )

        ext = _detect_image_ext(content)
        if not ext:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only valid jpg and png images are supported.")

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


@router.patch("/{location_id}")
async def update_location(
    location_id: int,
    payload: schemas.LocationUpdate,
    admin: User = Depends(get_current_admin),
):
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No update fields provided.")

    if "hints" in data and data["hints"] is not None:
        cleaned = [str(item).strip() for item in data["hints"] if str(item).strip()]
        if len(cleaned) > 3:
            raise HTTPException(status_code=400, detail="Maximum 3 hints allowed.")
        data["hints"] = cleaned or None

    updated = await services.update_location(location_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Location not found.")
    serialized = schemas.LocationRead.model_validate(updated).model_dump()
    return success_response(serialized, message="Location updated.")


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
async def delete_location(location_id: int, admin: User = Depends(get_current_admin)):
    deleted = await services.delete_location(location_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Location not found.")
    return success_response({}, message="Location deleted successfully.")