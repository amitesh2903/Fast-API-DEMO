import hashlib
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import jwt 
from models.blog import BlogModel , UpdateBlogModel, User
from config.config import blogs_collection, user_collection
from serializers.blog import DecodeBlogs, DecodeBlog
import datetime
from bson import ObjectId
from routes.constant import ConstantVariables
import toml
from routes.token import ALGORITHM, SECRET_KEY, create_access_token


with open('config.toml', 'r') as f:
    config = toml.load(f)

blog_root = APIRouter()

def custom_jsonable_encoder(data):
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, dict):
        return {key: custom_jsonable_encoder(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [custom_jsonable_encoder(item) for item in data]
    return data


def get_user_role(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        exp_timestamp = payload.get("exp")
        if exp_timestamp and datetime.datetime.now() > datetime.datetime.fromtimestamp(exp_timestamp):
            raise HTTPException(status_code=401, detail="Token has expired")
        
        user_role = payload.get("role")
        if user_role is None:
            raise HTTPException(status_code=401, detail="Token does not contain role information")

        return user_role
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@blog_root.get("/getdata")
async def get_data_using_token(request: Request):
    try:
        headers = request.headers
        if not headers:
            return Response(
                {"error": ConstantVariables.AUTHENTICATION_TOKEN_ERROR_MESSAGE},
                status=401
            )

        authorization_token = headers.get("authorization", None)

        if not authorization_token:
            return Response(
                {"error": ConstantVariables.AUTHENTICATION_TOKEN_ERROR_MESSAGE},
                status=401
            )

        user_auth_token = authorization_token.split(" ")[1]
        user_details = get_user_role(user_auth_token)
        return user_details
    
    except Exception as e:
        return JSONResponse(content={"error": "e"}, status_code=500)

# post request 
@blog_root.post("/new/blog")
async def NewBlog(doc:BlogModel,):
    try:

        doc = dict(doc)
        current_date = datetime.date.today()
        doc["date"] = str(current_date )
        
        res = blogs_collection.insert_one(doc)

        doc_id = str(res.inserted_id )

        return {
            "status" : "ok" ,
            "message" : "Blog posted successfully" , 
            "_id" : doc_id
        }
    
    except Exception as e:
        return {
            "status" : "error" ,
            "message" : str(e)
        }
    

# getting blogs 
@blog_root.get("/all/blogs")
async def AllBlogs():
    try:
        res =  blogs_collection.find() 
        decoded_data = DecodeBlogs(res)

        return {
            "status": "ok" , 
            "data" : decoded_data
        }
    except Exception as e:
        return {
            "status" : "error" ,
            "message" : str(e)
        }
    

# get blog using id
@blog_root.get("/blog/{_id}") 
async def Getblog(_id:str) :
    try:
        res = blogs_collection.find_one({"_id" : ObjectId(_id) }) 
        decoded_blog = DecodeBlog(res)
        return {
            "status" : "ok" ,
            "data" : decoded_blog
        }
    except Exception as e:
        return {
            "status" : "error" ,
            "message" : str(e)
        }


# update blog 
@blog_root.patch("/update/{_id}")
async def UpdateBlog(_id: str , doc:UpdateBlogModel):
    try:
        req = dict(doc.model_dump(exclude_unset=True)) 
        blogs_collection.find_one_and_update(
        {"_id" : ObjectId(_id) } ,
        {"$set" : req}
        )

        return {
            "status" : "ok" ,
            "message" : "blog updated successfully"
        }
    except Exception as e:
        return {
            "status" : "error" ,
            "message" : str(e)
        }


# delete blog 
@blog_root.delete("/delete/{_id}")
async def  DeleteBlog(_id : str, request: Request):
    try:
        headers = request.headers
        if not headers:
            return Response(
                {"error": ConstantVariables.AUTHENTICATION_TOKEN_ERROR_MESSAGE},
                status=401
            )

        authorization_token = headers.get("authorization", None)

        if not authorization_token:
            return Response(
                {"error": ConstantVariables.AUTHENTICATION_TOKEN_ERROR_MESSAGE},
                status=401
            )

        user_auth_token = authorization_token.split(" ")[1]
        user_details = get_user_role(user_auth_token)

        if user_details == "superadmin":
            
            data = blogs_collection.find_one_and_delete(
                {"_id" : ObjectId(_id)}
            )

            
            if data:
                return {
                    "status": "ok",
                    "message": "Blog deleted successfully"
                }
            else:
                # raise HTTPException(status_code=404, detail="Blog not found")
                return {
                    "status": 404,
                    "message": "Blog Not Found"
                }

        else:
            return JSONResponse(
                    content={"error": ConstantVariables.PERMISSION_ERROR_MESSAGE},
                    status_code=401
                )

    except Exception as e:
        return {
            "status" : "error" ,
            "message" : str(e)
        }

# Add users
@blog_root.post("/addusers/")
async def add_users(data: User):
    try:

        hashed_password = hashlib.sha1(data.password.encode('utf-8')).hexdigest()
        data.password = hashed_password

        user_dict = jsonable_encoder(data)

        result = user_collection.insert_one(user_dict)
        return {"message": "User added successfully", "user_id": str(result.inserted_id)}
    
    except Exception as e:
        logging.error(f"Error saving user: {e}")
        raise HTTPException(status_code=500, detail="Error saving user to the database")


@blog_root.get("/users/", response_model=List[User])
async def get_all_users():
    try:
        users = user_collection.find().to_list(length=100)
        return custom_jsonable_encoder(users)
    except Exception as e:
        logging.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving users from database")

# get blog using author name
@blog_root.get("/author/{author}")
async def GetBlogByAuthor(author:str):
    try:
        res = blogs_collection.find({"author" : author})
        decoded_data = DecodeBlogs(res)
        return {
            "status" : "ok" ,
            "data" : decoded_data
        }
    except Exception as e:
        return {
            "status" : "error" ,
            "message" : str(e)
        }

 

# Login user
@blog_root.get("/login")
async def login(email_address: str, password: str):
    try:        
        print("User Collection", )
        login_user = user_collection.find_one({"email": email_address})
        
        if login_user:
            hashed_password = hashlib.sha1(password.encode('utf-8')).hexdigest()
            
            if login_user['password'] == hashed_password:
                user_data = {"email": login_user['email'], "role": login_user['role']}
                access_token = create_access_token(data=user_data)
                print(f"TOKEN ==> {access_token}")
                role = get_user_role(access_token)

                return JSONResponse(
                    content={"message": "Login successful", "access_token": access_token, "role":role},
                    status_code=200
                )
            else:
                raise HTTPException(status_code=401, detail="Invalid email or password")
        else:
            return JSONResponse(content={"message": "Your email doesn't exist"}, status_code=404)

    except Exception as e:
        logging.error(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail="Error in login")
