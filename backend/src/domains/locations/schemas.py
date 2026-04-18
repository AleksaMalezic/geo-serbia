from pydantic import BaseModel


class LocationBase(BaseModel):
    name: str
    description: str | None = None
    hints: list[str] | None = None
    latitude: float
    longitude: float


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    hints: list[str] | None = None
    latitude: float | None = None
    longitude: float | None = None
    image_url: str | None = None
    is_approved: bool | None = None


class LocationRead(LocationBase):
    id: int
    image_url: str | None = None
    created_by_id: int | None = None
    is_approved: bool = False

    class Config:
        from_attributes = True