from pydantic import BaseModel, ConfigDict


class PostsIn(BaseModel):
    body: str


class PostsOut(PostsIn):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class CommentsIn(BaseModel):
    body: str
    post_id: int


class CommentsOut(CommentsIn):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


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
