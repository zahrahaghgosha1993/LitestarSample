from unittest.mock import ANY

from httpx import AsyncClient


async def test_create_note(client: AsyncClient) -> None:
    json = {"title": "test title"}
    response = await client.post(
        "/notes", json=json
    )
    assert response.json() == {
        "id": ANY,
        "title": json['title']
    }
