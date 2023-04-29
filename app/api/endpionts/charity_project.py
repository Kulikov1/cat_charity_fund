from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_project_has_no_invested_money,
                                check_project_is_exists,
                                check_project_is_not_close,
                                check_unique_project_name, check_updating_data,
                                check_valid_updated_amount)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (CharityProjectBase, CharityProjectBD,
                                         CharityProjectUpdate)
from app.services.donation_to_project import check_not_fully_invested_donations

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectBD,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def create_charity_project(
    charity_project: CharityProjectBase,
    session: AsyncSession = Depends(get_async_session),
):
    """Доступно только суперюзеру"""

    await check_unique_project_name(charity_project, session)
    new_project = await charity_project_crud.create(
        charity_project, session)
    await check_not_fully_invested_donations(new_project, session)
    await session.refresh(new_project)
    return new_project


@router.get(
    '/',
    response_model=List[CharityProjectBD],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    all_charity_projects = await charity_project_crud.get_multi(session)
    return all_charity_projects


@router.delete(
    '/{project_id}',
    response_model=CharityProjectBD,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Доступно только суперюзеру"""

    charity_project = await check_project_is_exists(
        project_id, session
    )
    charity_project = await check_project_has_no_invested_money(
        charity_project
    )
    charity_project = await check_project_is_not_close(
        charity_project
    )
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectBD,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Доступно только суперюзеру"""

    charity_project = await check_project_is_exists(
        project_id, session
    )
    charity_project = await check_project_is_not_close(
        charity_project
    )
    charity_project = await check_valid_updated_amount(
        charity_project, obj_in
    )
    await check_updating_data(obj_in, session)
    charity_project = await charity_project_crud.update(
        db_obj=charity_project,
        obj_in=obj_in,
        session=session
    )
    return charity_project
