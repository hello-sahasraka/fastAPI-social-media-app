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
    logger.info(f"Finding post with id: {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(f"Executing query: {query}")
    return await database.fetch_one(query)


@router.post("/", response_model=PostsOut, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostsIn):
    logger.info("Creating a new post")
    data = post.model_dump()
    query = post_table.insert().values(data)
    logger.debug(f"Executing query: {query}")
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/", response_model=list[PostsOut])
async def get_all_post():
    logger.info("Fetching all posts")
    query = post_table.select()
    logger.debug(f"Executing query: {query}")
    return await database.fetch_all(query)


@router.post("/comment", response_model=CommentsOut, status_code=status.HTTP_200_OK)
async def create_comment(comment: CommentsIn):
    logger.info(f"Creating comment for post id: {comment.post_id}")
    post = await findPost(comment.post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    query = comments_table.insert().values(data)
    logger.debug(f"Executing query: {query}")
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/{post_id}/comment", response_model=list[CommentsOut])
async def get_post_comments(post_id: int):
    logger.info(f"Fetching comments for post id: {post_id}")
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    logger.debug(f"Executing query: {query}")
    return await database.fetch_all(query)


@router.get("/{post_id}", response_model=UserPostsWithCommentsResponse)
async def get_post_with_comments(post_id: int):
    logger.info(f"Fetching post with id: {post_id} and its comments")
    post = await findPost(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "post": post,
        "comments": await get_post_comments(post_id),
    }
