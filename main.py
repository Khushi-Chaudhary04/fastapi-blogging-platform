from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from typing import List
from models import Post, Comment

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["blogging_platform"]
posts_collection = db["posts"]

# Create FastAPI instance
app = FastAPI()

# API endpoints
@app.post("/posts/", response_model=Post)
async def create_post(post: Post):
    new_post = dict(post)
    new_post.pop("comments", None)  # Removing comments field since it's not a part of the post document
    result = posts_collection.insert_one(new_post)
    post.id = str(result.inserted_id)
    return post

@app.get("/posts/", response_model=List[Post])
async def read_posts():
    posts = []
    for post in posts_collection.find():
        post["_id"] = str(post["_id"])
        posts.append(post)
    return posts

@app.get("/posts/{post_id}", response_model=Post)
async def read_post(post_id: str):
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if post:
        post["_id"] = str(post["_id"])
        return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: str, post: Post):
    updated_post = dict(post)
    updated_post.pop("comments", None)
    result = posts_collection.replace_one({"_id": ObjectId(post_id)}, updated_post)
    if result.modified_count == 1:
        return updated_post
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    result = posts_collection.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 1:
        return {"message": "Post deleted successfully"}
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts/{post_id}/comments/", response_model=Post)
async def create_comment(post_id: str, comment: Comment):
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if post:
        comment_dict = dict(comment)
        post["comments"].append(comment_dict)
        result = posts_collection.replace_one({"_id": ObjectId(post_id)}, post)
        if result.modified_count == 1:
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts/{post_id}/like/")
async def like_post(post_id: str):
    result = posts_collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"likes": 1}})
    if result.modified_count == 1:
        return {"message": "Post liked successfully"}
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts/{post_id}/dislike/")
async def dislike_post(post_id: str):
    result = posts_collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"dislikes": 1}})
    if result.modified_count == 1:
        return {"message": "Post disliked successfully"}
    raise HTTPException(status_code=404, detail="Post not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000
                )
