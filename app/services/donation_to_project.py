from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def donation_to_project_func(
    session: AsyncSession,
) -> None:
    donation = await session.execute(
        select(Donation).where(
            Donation.fully_invested == False
        )
    )
    donation = donation.scalars().first()
    charity_project = await session.execute(
        select(CharityProject).where(
            CharityProject.fully_invested == False
        )
    )
    charity_project = charity_project.scalars().first()
    if not donation or not charity_project:
        return
    ost_donation = donation.full_amount - donation.invested_amount
    print(ost_donation)
    charity_project.invested_amount += ost_donation
    if charity_project.invested_amount <= charity_project.full_amount:
        donation.invested_amount = donation.full_amount
        donation.fully_invested = True
        donation.close_date = datetime.now()
    else:
        print(charity_project.invested_amount)
        donation.invested_amount += ost_donation - (
            charity_project.invested_amount - charity_project.full_amount
        )
    if charity_project.invested_amount >= charity_project.full_amount:
        charity_project.invested_amount = charity_project.full_amount
        charity_project.fully_invested = True
        charity_project.close_date = datetime.now()
    await session.commit()
    await donation_to_project_func(session)
