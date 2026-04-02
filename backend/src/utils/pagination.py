from fastapi import Query


def get_pagination_params(
    page: int = Query(1, ge=1, description="page number"),
    limit: int = Query(10, ge=1, le=100, description="number of items per page")
):
    skip = (page - 1) * limit
    return {"page": page, "skip": skip, "limit": limit}
