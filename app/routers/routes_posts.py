from fastapi import APIRouter, HTTPException
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


post_table = {}
comments_table = {}


def findPost(post_id: int):
    return post_table.get(post_id)


@router.post("/", response_model=PostsOut)
async def create_post(post: PostsIn):
    data = post.model_dump()
    last_record_id = len(post_table)
    new_id = last_record_id + 1
    new_post = {**data, "id": new_id}
    post_table[new_id] = new_post
    return new_post


@router.get("/", response_model=list[PostsOut])
async def get_all_post():
    return list(post_table.values())


@router.post("/comment", response_model=CommentsOut)
async def create_comment(comment: CommentsIn):
    post = findPost(comment.post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    last_record_id = len(comments_table)
    new_id = last_record_id + 1
    new_comment = {**data, "id": new_id}
    comments_table[new_id] = new_comment
    return new_comment


@router.get("/{post_id}/comment", response_model=list[CommentsOut])
async def get_post_comments(post_id: int):
    return [
        comment for comment in comments_table.values() if comment["post_id"] == post_id
    ]


@router.get("/{post_id}", response_model=UserPostsWithCommentsResponse)
async def get_post_with_comments(post_id: int):
    post = findPost(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "post": post,
        "comments": await get_post_comments(post_id),
    }
