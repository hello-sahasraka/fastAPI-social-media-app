from pydantic import BaseModel, ConfigDict
from typing import Optional


class PostsIn(BaseModel):
    body: str


class PostsOut(PostsIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    image_url: Optional[str] = None


class CommentsIn(BaseModel):
    body: str
    post_id: int


class CommentsOut(CommentsIn):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int


class UserPostsWithLikes(PostsOut):
    likes: int


class UserPostsWithComments(BaseModel):
    post: UserPostsWithLikes
    comments: list[CommentsOut]


class UserPostsWithCommentsResponse(BaseModel):
    post: UserPostsWithLikes
    comments: list[CommentsOut]


class PostLikeIn(BaseModel):
    post_id: int


class PostLikeOut(PostLikeIn):
    id: int
    user_id: int
