__all__ = ["SellerService"]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.sellers import Seller
from src.schemas.sellers import IncomingSeller, UpdateSeller


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_seller(self, seller: IncomingSeller) -> Seller:
        new_seller = Seller(
            **{
                "first_name": seller.first_name,
                "last_name": seller.last_name,
                "e_mail": seller.e_mail,
                "password": seller.password,
            }
        )

        self.session.add(new_seller)
        await self.session.flush()

        return new_seller

    async def get_all_sellers(self) -> list[Seller]:
        query = select(Seller)
        result = await self.session.execute(query)

        return result.scalars().all()

    async def get_single_seller(self, seller_id: int) -> Seller | None:
        query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_seller(self, seller_id: int, payload: UpdateSeller) -> Seller | None:
        if seller := await self.session.get(Seller, seller_id):
            seller.first_name = payload.first_name
            seller.last_name = payload.last_name
            seller.e_mail = payload.e_mail

            await self.session.flush()
            return seller

    async def delete_seller(self, seller_id: int) -> bool:
        seller = await self.session.get(Seller, seller_id)

        if seller:
            await self.session.delete(seller)
            await self.session.flush()
            return True

        return False
