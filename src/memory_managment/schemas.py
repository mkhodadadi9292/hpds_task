from pydantic import BaseModel


class MemorySchema(BaseModel):
    total: int
    free: int
    used: int

    class Config:
        from_attributes = True
