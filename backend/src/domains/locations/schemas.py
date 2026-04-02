from pydantic import BaseModel


class LocationBase(BaseModel):
    name: str
    description: str | None = None
    hints: list[str] | None = None
    latitude: float
    longitude: float


class LocationCreate(LocationBase):
    pass


class LocationRead(LocationBase):
    id: int
    image_url: str | None = None

    class Config:
        from_attributes = True
