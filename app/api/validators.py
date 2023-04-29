from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import CharityProjectUpdate
from app.models.charity_project import CharityProject


async def check_unique_project_name(
    charity_project: CharityProjectUpdate,
    session: AsyncSession,
) -> None:
    charity_project = await session.execute(
        select(CharityProject).where(
            CharityProject.name == charity_project.name
        )
    )
    if charity_project.scalars().first():
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!')


async def check_project_is_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_project_crud.get(
        project_id, session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    return charity_project


async def check_project_has_no_invested_money(
    charity_project: CharityProject,
) -> CharityProject:
    if charity_project.invested_amount != 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return charity_project


async def check_project_is_not_close(
    charity_project: CharityProject,
) -> CharityProject:
    if charity_project.fully_invested is True:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )
    return charity_project


async def check_valid_updated_amount(
    charity_project: CharityProject,
    obj_in: CharityProjectUpdate,
) -> CharityProject:
    if obj_in.full_amount is not None:
        if obj_in.full_amount < charity_project.invested_amount:
            raise HTTPException(
                status_code=422,
                detail='Итоговая сумма не может быть меньше уже внесенной суммы'
            )
        if obj_in.full_amount == charity_project.invested_amount:
            charity_project.fully_invested = True
            charity_project.close_date = datetime.now()
    return charity_project


async def check_updating_data(
    obj_in: CharityProjectUpdate,
    session: AsyncSession,
) -> None:
    await check_unique_project_name(obj_in, session)
    for field, value in obj_in:
        if value == '':
            raise HTTPException(
                status_code=422,
                detail='Поле {field} не должно быть пустым!'
            )
