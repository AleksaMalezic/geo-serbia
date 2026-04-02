from typing import Any, Generic, TypeVar

T = TypeVar("T")


class PaginatedData(Generic[T]):
    items: list[T]
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int


class StandardResponse(Generic[T]):
    success: bool
    status: int
    message: str
    data: T


def success_response(data: Any, message: str = "Success", status: int = 200):
    return {
        "success": True,
        "status": status,
        "message": message,
        "data": data,
    }


def paginated_response(
    items: list,
    page: int,
    limit: int,
    total_items: int,
    message: str = "Items listed.",
):
    total_pages = (total_items + limit - 1) // limit if limit else 1

    return {
        "success": True,
        "status": 200,
        "message": message,
        "data": {
            "items": items,
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items_per_page": limit,
        },
    }
