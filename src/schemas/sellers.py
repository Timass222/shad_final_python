from pydantic import BaseModel, ConfigDict

__all__ = [
    "IncomingSeller",
    "UpdateSeller",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "ReturnedAllSellers",
]


class SellerBook(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    year: int
    pages: int
    seller_id: int


class IncomingSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str
    password: str


class UpdateSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


class ReturnedSeller(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    e_mail: str


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[SellerBook]


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
