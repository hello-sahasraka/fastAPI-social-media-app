
import logging
from fastapi import APIRouter, HTTPException
from app.database import post_table, comments_table, database
from fastapi import status
from app.models.posts import (
    PostsIn,
    PostsOut,
    CommentsIn,
    CommentsOut,
    UserPostsWithCommentsResponse,
)

router = APIRouter(
    prefix="/post",
    tags=["posts"],
)

logger = logging.getLogger(__name__)

async def findPost(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("/", response_model=PostsOut, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostsIn):
    data = post.model_dump()
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/", response_model=list[PostsOut])
async def get_all_post():
    query = post_table.select()
    return await database.fetch_all(query)


@router.post("/comment", response_model=CommentsOut, status_code=status.HTTP_200_OK)
async def create_comment(comment: CommentsIn):
    post = await findPost(comment.post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    query = comments_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/{post_id}/comment", response_model=list[CommentsOut])
async def get_post_comments(post_id: int):
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    return await database.fetch_all(query)


@router.get("/{post_id}", response_model=UserPostsWithCommentsResponse)
async def get_post_with_comments(post_id: int):
    post = await findPost(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "post": post,
        "comments": await get_post_comments(post_id),
    }
