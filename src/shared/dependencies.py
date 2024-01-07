from database.database import get_session
from fastapi import Depends, HTTPException, status
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..hub.models import Hubs, HubShifts
from .schemas import HubShiftValidation


class HubValidator:
    async def __call__(self, hub_id: int, session: AsyncSession = Depends(get_session)):
        hub: Hubs = await self.validate_hub_id(session, hub_id)
        return hub

    async def validate_hub_id(self, session: AsyncSession, hub_id: int):
        query_results: Result = await session.execute(
            select(Hubs).where(Hubs.id == hub_id)
        )
        hub: Hubs = query_results.scalars().first()
        if hub is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid HubID."
            )
        return hub


class HubShiftValidator:
    async def __call__(
        self, hub_id: int, shift_id: int, session: AsyncSession = Depends(get_session)
    ):
        hub: Hubs = await self.validate_hub_id(session, hub_id)
        shift: HubShifts = await self.validate_shift_id(session, shift_id)
        return HubShiftValidation(hub=hub, shift=shift)

    async def validate_hub_id(self, session: AsyncSession, hub_id: int):
        query_results: Result = await session.execute(
            select(Hubs).where(Hubs.id == hub_id)
        )
        hub: Hubs = query_results.scalars().first()
        if hub is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid HubID."
            )
        return hub

    async def validate_shift_id(self, session: AsyncSession, shift_id: int):
        query_results: Result = await session.execute(
            select(HubShifts).where(HubShifts.id == shift_id)
        )
        shift: Hubs = query_results.scalars().first()
        if shift is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid ShiftID."
            )
        return shift
