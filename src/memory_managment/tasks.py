from .models import Memory
from fastapi import BackgroundTasks
from fastapi_utilities import repeat_every
from database.database import async_session_maker
import os


@repeat_every(seconds=5)
async def add_memory_info(r=None):

    # Getting all memory using os.popen()
    total_memory, used_memory, free_memory = map(
        int, os.popen('free -t -m').readlines()[-1].split()[1:])

    async with async_session_maker() as session:
        memory_info = Memory(total=total_memory,
                             used=used_memory,
                             free=free_memory)
        session.add(memory_info)
        await session.commit()
