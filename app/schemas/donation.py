from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Extra, Field, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationGetByUser(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationBD(DonationBase):
    id: int
    invested_amount: int = Field(0)
    fully_invested: bool = Field(False)
    create_date: datetime
    close_date: Optional[datetime] = Field(None)
    user_id: int

    class Config:
        orm_mode = True
