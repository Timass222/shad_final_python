import pytest
from fastapi import status

API_SELLERS_URL_PREFIX = "/api/v1/seller"
API_BOOKS_URL_PREFIX = "/api/v1/books"


async def create_seller_via_api(async_client, suffix: str = "1") -> dict:
    payload = {
        "first_name": "Ivan",
        "last_name": "Petrov",
        "e_mail": f"ivan{suffix}@example.com",
        "password": "qwerty123",
    }
    response = await async_client.post(f"{API_SELLERS_URL_PREFIX}/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.mark.asyncio()
async def test_create_seller(async_client):
    payload = {
        "first_name": "Anna",
        "last_name": "Ivanova",
        "e_mail": "anna@example.com",
        "password": "secret-pass",
    }

    response = await async_client.post(f"{API_SELLERS_URL_PREFIX}/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert data["e_mail"] == payload["e_mail"]
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio()
async def test_get_all_sellers(async_client):
    await create_seller_via_api(async_client, "all-1")
    await create_seller_via_api(async_client, "all-2")

    response = await async_client.get(f"{API_SELLERS_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "sellers" in data
    assert len(data["sellers"]) == 2
    assert all("password" not in seller for seller in data["sellers"])


@pytest.mark.asyncio()
async def test_get_single_seller_with_books(async_client):
    seller = await create_seller_via_api(async_client, "with-books")

    payload_book_1 = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 320,
        "year": 2025,
        "seller_id": seller["id"],
    }
    payload_book_2 = {
        "title": "Refactoring",
        "author": "Martin Fowler",
        "count_pages": 450,
        "year": 2024,
        "seller_id": seller["id"],
    }

    response_book_1 = await async_client.post(f"{API_BOOKS_URL_PREFIX}/", json=payload_book_1)
    response_book_2 = await async_client.post(f"{API_BOOKS_URL_PREFIX}/", json=payload_book_2)

    assert response_book_1.status_code == status.HTTP_201_CREATED
    assert response_book_2.status_code == status.HTTP_201_CREATED

    response = await async_client.get(f"{API_SELLERS_URL_PREFIX}/{seller['id']}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == seller["id"]
    assert data["first_name"] == seller["first_name"]
    assert data["last_name"] == seller["last_name"]
    assert data["e_mail"] == seller["e_mail"]
    assert "password" not in data

    assert "books" in data
    assert len(data["books"]) == 2
    assert all(book["seller_id"] == seller["id"] for book in data["books"])


@pytest.mark.asyncio()
async def test_update_seller(async_client):
    seller = await create_seller_via_api(async_client, "update")

    update_payload = {
        "first_name": "Petr",
        "last_name": "Sidorov",
        "e_mail": "petr.sidorov@example.com",
    }

    response = await async_client.put(f"{API_SELLERS_URL_PREFIX}/{seller['id']}", json=update_payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == seller["id"]
    assert data["first_name"] == update_payload["first_name"]
    assert data["last_name"] == update_payload["last_name"]
    assert data["e_mail"] == update_payload["e_mail"]
    assert "password" not in data


@pytest.mark.asyncio()
async def test_delete_seller_cascades_books(async_client):
    seller = await create_seller_via_api(async_client, "delete")

    payload_book = {
        "title": "Domain-Driven Design",
        "author": "Eric Evans",
        "count_pages": 560,
        "year": 2025,
        "seller_id": seller["id"],
    }

    create_book_response = await async_client.post(f"{API_BOOKS_URL_PREFIX}/", json=payload_book)
    assert create_book_response.status_code == status.HTTP_201_CREATED

    delete_response = await async_client.delete(f"{API_SELLERS_URL_PREFIX}/{seller['id']}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    get_seller_response = await async_client.get(f"{API_SELLERS_URL_PREFIX}/{seller['id']}")
    assert get_seller_response.status_code == status.HTTP_404_NOT_FOUND

    all_books_response = await async_client.get(f"{API_BOOKS_URL_PREFIX}/")
    assert all_books_response.status_code == status.HTTP_200_OK
    assert all_books_response.json() == {"books": []}
