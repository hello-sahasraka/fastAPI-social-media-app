from pydantic import BaseModel, ConfigDict


class PostsIn(BaseModel):
    body: str


class PostsOut(PostsIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CommentsIn(BaseModel):
    body: str
    post_id: int


class CommentsOut(CommentsIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserPostsWithComments(BaseModel):
    post: PostsOut
    comments: list[CommentsOut]


class UserPostsWithCommentsResponse(BaseModel):
    post: PostsOut
    comments: list[CommentsOut]
