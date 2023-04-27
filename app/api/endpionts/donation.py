from typing import List
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession


from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models import User
from app.services.donation_to_project import donation_to_project_func
from app.schemas.donation import (
    DonationBase, DonationBD, DonationGetByUser
)


router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationBD],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.post(
    '/',
    response_model=DonationGetByUser,
    response_model_exclude_none=True,
)
async def create_donation(
    donation: DonationBase,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    new_donation = await donation_crud.create(
        donation, session, user
    )
    await donation_to_project_func(session)
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/my',
    response_model=List[DonationGetByUser],
)
async def get_user_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    donations = await donation_crud.get_by_user(user, session)
    return donations