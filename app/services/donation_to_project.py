from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def check_not_fully_invested_projects(
    donation: Donation,
    session: AsyncSession
) -> None:
    """При создании пожертвования функция проверяет незаполненные
    проекты и распределяет в них сумму пожертвования
    """

    donation_fully_invested = False
    donation_full_amount = donation.full_amount
    donation_invested_amount = donation.invested_amount
    while donation_fully_invested is not True:
        charity_project = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested == False # noqa
            )
        )
        charity_project = charity_project.scalars().first()
        if not charity_project:
            break
        rest_donation = donation_full_amount - donation_invested_amount
        charity_project.invested_amount += rest_donation
        if charity_project.invested_amount <= charity_project.full_amount:
            donation_invested_amount = donation_full_amount
            donation_fully_invested = True
            donation.close_date = datetime.now()
        else:
            donation_invested_amount += rest_donation - (
                charity_project.invested_amount - charity_project.full_amount
            )
        if charity_project.invested_amount >= charity_project.full_amount:
            charity_project.invested_amount = charity_project.full_amount
            charity_project.fully_invested = True
            charity_project.close_date = datetime.now()
        await session.commit()
    donation.full_amount = donation_full_amount
    donation.invested_amount = donation_invested_amount
    donation.fully_invested = donation_fully_invested
    await session.commit()


async def check_not_fully_invested_donations(
    project: CharityProject,
    session: AsyncSession
) -> None:
    """При создании проекта функция проверяет нераспределенные
    пожертвования и вносит их в проект
    """

    project_fully_invested = False
    project_full_amount = project.full_amount
    project_invested_amount = project.invested_amount
    while project_fully_invested is not True:
        donation = await session.execute(
            select(Donation).where(
                Donation.fully_invested == False # noqa
            )
        )
        donation = donation.scalars().first()
        if not donation:
            break
        rest_donation = donation.full_amount - donation.invested_amount
        project_invested_amount += rest_donation
        if project_invested_amount <= project_full_amount:
            donation.invested_amount = donation.full_amount
            donation.fully_invested = True
            donation.close_date = datetime.now()
        else:
            donation.invested_amount += rest_donation - (
                project_invested_amount - project_full_amount
            )
        if project_invested_amount >= project_full_amount:
            project_invested_amount = project_full_amount
            project_fully_invested = True
            project.close_date = datetime.now()
        await session.commit()
    project.full_amount = project_full_amount
    project.invested_amount = project_invested_amount
    project.fully_invested = project_fully_invested
    await session.commit()
