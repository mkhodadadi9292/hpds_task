from pydantic import BaseModel


class MemoryModel(BaseModel):
    total: int
    free: int
    used: int

    class Config:
        from_attributes = True
