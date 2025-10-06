from pydantic import BaseModel
import pytest
from httpx import AsyncClient
from app import security

from app.test.helpers import create_post, create_comment, create_like

class PostSchema(BaseModel):
    body: str
    id: int


@pytest.fixture()
def mock_generate_cute_creature_api(mocker):
    return mocker.patch(
        "app.tasks._generate_cute_creature_api",
        return_value={"output_url": "https://example.com/image.jpg"},
    ) 


@pytest.fixture()
async def created_comment(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
):
    return await create_comment(
        "Test comment", created_post["id"], async_client, logged_in_token
    )


@pytest.mark.anyio
async def test_create_post(
    async_client: AsyncClient, confirm_user: dict, logged_in_token: str
):
    body = "Test post"

    response = await async_client.post(
        "/post/",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    data = response.json()

    assert response.status_code == 201
    assert data["body"] == body
    assert "id" in data and isinstance(data["id"], int)
    assert {
        "id": 1,
        "body": body,
        "user_id": confirm_user["id"],
        "image_url": None,
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_with_prompt(
    async_client: AsyncClient, logged_in_token: str, mock_generate_cute_creature_api
):
    body = "Test post"

    response = await async_client.post(
        "/post/?prompt=A cat",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    ) 

    assert response.status_code == 201
    assert {
        "id": 1,
        "body": body,
        "image_url": None,
    }.items() <= response.json().items()
    mock_generate_cute_creature_api.assert_called()



@pytest.mark.anyio
async def test_like_post(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
):
    response = await async_client.post(
        "/post/like",
        json={"post_id": created_post["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 201


@pytest.mark.anyio
async def test_create_post_expired_token(
    async_client: AsyncClient, confirm_user: dict, mocker
):
    mocker.patch("app.security.access_token_expire_minutes", return_value=-1)
    token = security.create_access_token(confirm_user["email"])
    response = await async_client.post(
        "/post/",
        json={"body": "Test Post"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]


@pytest.mark.anyio
async def test_create_post_missing_data(
    async_client: AsyncClient, logged_in_token: str
):
    response = await async_client.post(
        "/post/",
        json={},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "sorting, expected_order",
    [
        ("new", [3, 2, 1]),
        ("old", [1, 2, 3]),
    ],
)
async def test_get_all_posts_sorting(
    async_client: AsyncClient,
    logged_in_token: str,
    sorting: str,
    expected_order: list[int],
):
    await create_post("Test post_1", async_client, logged_in_token)
    await create_post("Test post_2", async_client, logged_in_token)
    await create_post("Test post_3", async_client, logged_in_token)

    response = await async_client.get("/post/", params={"sorting": sorting})
    assert response.status_code == 200

    data = response.json()
    post_ids = [post["id"] for post in data]

    assert post_ids == expected_order


@pytest.mark.anyio
async def test_get_all_posts_sort_likes(
    async_client: AsyncClient, logged_in_token: str
):
    await create_post("Test post_1", async_client, logged_in_token)
    await create_post("Test post_2", async_client, logged_in_token)

    await create_like(1, async_client, logged_in_token)

    response = await async_client.get("/post/", params={"sorting": "most_likes"})
    assert response.status_code == 200

    data = response.json()
    post_ids = [post["id"] for post in data]
    expected_order = [1, 2]
    assert post_ids == expected_order


@pytest.mark.anyio
async def test_get_all_posts_wrong_sorting(async_client: AsyncClient):
    response = await async_client.get("/post/", params={"sorting": "wrong_sort"})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_post(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/post/")

    assert response.status_code == 200
    assert created_post in response.json()


@pytest.mark.anyio
async def test_create_comment(
    async_client: AsyncClient,
    created_post: dict,
    confirm_user: dict,
    logged_in_token: str,
):
    body = "Test comment"
    post_id = created_post["id"]

    response = await async_client.post(
        "/post/comment",
        json={"body": body, "post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["body"] == body
    assert {
        "id": 1,
        "body": body,
        "post_id": created_post["id"],
        "user_id": confirm_user["id"],
    }.items() <= response.json().items()
    assert "id" in data and isinstance(data["id"], int)
    assert "post_id" in data and isinstance(data["post_id"], int)


@pytest.mark.anyio
async def test_create_comment_post_not_found(
    async_client: AsyncClient, logged_in_token: str
):
    body = "Test comment"
    post_id = 99

    response = await async_client.post(
        "/post/comment",
        json={"body": body, "post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_comment_missing_data(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
):
    post_id = created_post["id"]

    response = await async_client.post(
        "/post/comment",
        json={"post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_post_with_comments(async_client: AsyncClient, created_comment: dict):
    post_id: int = created_comment["post_id"]

    response = await async_client.get(f"/post/{post_id}")
    print(response.json())

    assert response.status_code == 200
