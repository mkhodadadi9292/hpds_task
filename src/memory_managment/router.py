from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from database.database import get_session
from .models import Memory
from .schemas import MemoryModel
from .tasks import add_memory_info
from ..auth.dependencies import get_only_superadmin, get_current_user
from ..auth.models import Users

router = APIRouter(tags=["MemoryManager"])


@router.post("/start_service/", description="Trigger a background task to store memory usage data.")
async def start_service(background_tasks: BackgroundTasks, user: Users = Depends(get_only_superadmin)):
    background_tasks.add_task(add_memory_info)
    return {"message": "Service is started..."}


@router.get("/memory/{limit}", description="Get last memory usage records from the database based on the given limit",
            response_model=List[MemoryModel])
async def get_last_memory(limit: int, user: Users = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    query_set = select(Memory).order_by(desc("id")).limit(limit)
    results: List[Memory] = await session.execute(query_set)
    return results
