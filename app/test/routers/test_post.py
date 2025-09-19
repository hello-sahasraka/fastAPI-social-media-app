from pydantic import BaseModel
import pytest
from httpx import AsyncClient


class PostSchema(BaseModel):
    body: str
    id: int

async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/post/", json={"body": body})
    return response.json()


async def create_comment(body: str, post_id: int, async_client: AsyncClient) -> dict:
    response = await async_client.post("/post/comment", json={"body": body, "post_id": post_id})
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient):
    return await create_post("Test post", async_client)

@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict):
    return await create_comment("Test comment", created_post["id"], async_client)

@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient):
    body = "Test post"

    response = await async_client.post("/post/", json={"body": body})

    assert response.status_code == 201
    assert {"id": 1, "body": body}.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_missing_data(async_client: AsyncClient):
    response = await async_client.post("/post/", json={})

    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_post(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/post/")

    assert response.status_code == 200
    assert response.json() == [created_post]


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    body = "Test comment"
    post_id = created_post["id"]

    response = await async_client.post("/post/comment", json={"body": body, "post_id": post_id})

    assert response.status_code == 200
    assert {"id": 1, "body": body, "post_id": post_id}.items() <= response.json().items()

@pytest.mark.anyio
async def test_create_comment_post_not_found(async_client: AsyncClient):
    body = "Test comment"
    post_id = 99

    response = await async_client.post("/post/comment", json={"body": body, "post_id": post_id})

    assert response.status_code == 404

@pytest.mark.anyio
async def test_create_comment_missing_data(async_client: AsyncClient,  created_post: dict):
    post_id = created_post["id"]

    response = await async_client.post("/post/comment", json={"post_id": post_id})

    assert response.status_code == 422

@pytest.mark.anyio
async def test_get_post_with_comments(async_client: AsyncClient, created_comment: dict):
    post_id: int = created_comment["post_id"]

    response = await async_client.get(f"/post/{post_id}")
    print(response.json())

    assert response.status_code == 200
