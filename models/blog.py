from typing import Union
from bson import ObjectId
from fastapi import FastAPI
from pydantic import BaseModel

class BlogModel(BaseModel):
    title : str 
    sub_title : str 
    content : str 
    author : str
    tags : list 

class UpdateBlogModel(BaseModel):
    title : str  = None
    sub_title : str  = None 
    content : str  = None 
    author : str = None 
    tags : list = None


class User(BaseModel):
    _id: str
    name: str
    email: str
    # password: str
    role: str = None

class UserLogin(BaseModel):
    name: str
    email: str
    password: str
    role: str
    authtoken: str