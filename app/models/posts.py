from pydantic import BaseModel


class PostsIn(BaseModel):
    body: str


class PostsOut(PostsIn):
    id: int


class CommentsIn(BaseModel):
    body: str
    post_id: int


class CommentsOut(CommentsIn):
    id: int


class UserPostsWithComments(BaseModel):
    post: PostsOut
    comments: list[CommentsOut]


class UserPostsWithCommentsResponse(BaseModel):
    post: PostsOut
    comments: list[CommentsOut]
