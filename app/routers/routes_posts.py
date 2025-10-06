import logging
import sqlalchemy
from enum import Enum
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Request 
from app.database import post_table, comments_table, likes_table, database
from app.models.posts import (
    PostsIn,
    PostsOut,
    PostLikeIn,
    PostLikeOut,
    CommentsIn,
    CommentsOut,
    UserPostsWithCommentsResponse,
    UserPostsWithLikes,
)
from typing import Annotated
from app.models.users import UserIn
from app.security import get_current_user
from app.tasks import generate_and_add_to_post

router = APIRouter(
    prefix="/post",
    tags=["posts"],
)

logger = logging.getLogger(__name__)

select_post_and_likes = (
    sqlalchemy.select(
        post_table, sqlalchemy.func.count(likes_table.c.id).label("likes")
    )
    .select_from(post_table.outerjoin(likes_table))
    .group_by(post_table.c.id)
)


async def findPost(post_id: int):
    logger.info(f"Finding post with id: {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(f"Executing query: {query}")
    return await database.fetch_one(query)


@router.post("/", response_model=PostsOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostsIn, current_user: Annotated[UserIn, Depends(get_current_user)], background_task: BackgroundTasks, request: Request, prompt: str = None
):
    logger.info("Creating a new post")
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    logger.debug(f"Executing query: {query}")
    last_record_id = await database.execute(query)

    if prompt:
        background_task.add_task(
            generate_and_add_to_post,
            current_user.email,
            last_record_id,
            request.url_for("get_post_with_comments", post_id = last_record_id),
            database,
            prompt
        )

    return {**data, "id": last_record_id}


class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"


@router.get(
    "/", response_model=list[UserPostsWithLikes], status_code=status.HTTP_200_OK
)
async def get_all_post(sorting: PostSorting = PostSorting.new):
    logger.info("Fetching all posts")

    if sorting == PostSorting.new:
        query = select_post_and_likes.order_by(post_table.c.id.desc())
    elif sorting == PostSorting.old:
        query = select_post_and_likes.order_by(post_table.c.id.asc())
    elif sorting == PostSorting.most_likes:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))
    logger.debug(f"Executing query: {query}")
    return await database.fetch_all(query)


@router.post("/comment", response_model=CommentsOut, status_code=status.HTTP_200_OK)
async def create_comment(
    comment: CommentsIn, current_user: Annotated[UserIn, Depends(get_current_user)]
):
    logger.info(f"Creating comment for post id: {comment.post_id}")
    post = await findPost(comment.post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**comment.model_dump(), "user_id": current_user.id}
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

    query = select_post_and_likes.where(post_table.c.id == post_id)
    logger.debug(f"Executing query: {query}")

    post = await database.fetch_one(query)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "post": post,
        "comments": await get_post_comments(post_id),
    }


@router.post("/like", response_model=PostLikeOut, status_code=status.HTTP_201_CREATED)
async def like_post(
    like: PostLikeIn, current_user: Annotated[UserIn, Depends(get_current_user)]
):
    logger.info("Liking post")

    post = await findPost(like.post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    data = {**like.model_dump(), "user_id": current_user.id}
    query = likes_table.insert().values(data)
    logger.debug(f"Executing query: {query}")
    last_recorded_id = await database.execute(query)

    return {**data, "id": last_recorded_id}
