from pydantic import BaseModel
from typing import List

class Comment(BaseModel):
    text: str
    user_id: str

class Post(BaseModel):
    title: str
    content: str
    author_id: str
    comments: List[Comment] = []
    likes: int = 0
    dislikes: int = 0
