from typing import Optional
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
import pymongo
import json
from bson.json_util import dumps


app = FastAPI()
client = pymongo.MongoClient("mongodb://localhost:27017/")
DB = client["pymongodb"]
userCollection = DB["user"]

def ResponseModel(success: bool, message: str, data=[]):
    return jsonable_encoder(
        {
            "data": data,
            "code": 200,
            "succes": success,
            "message": message,
        }
    )


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}


class User(BaseModel):
    name: str = Field(examples=["Foo"])
    email: str = Field(examples=["Foo@mail.com"])

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "jdoe@x.edu.ng",
            }
        }


class GetSingleUserByMail(BaseModel):
    email: str = Field(examples=["Foo@mail.com"])
    class Config:
        json_schema_extra = {
            "example": {
                "email": "jdoe@x.edu.ng",
            }
        }


class UpdateUser(BaseModel):
    name: Optional[str]
    email: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "jdoe@x.edu.ng",
            }
        }


# SIGNUP
@app.post("/signup")
def signup(item: User):
    existUser = json.loads(dumps(userCollection.find({"email": item.email})))
    if existUser and len(existUser) > 0:
        return existUser
    else:
        insertData = json.loads(
            dumps(userCollection.insert_one(jsonable_encoder(item)))
        )
        if insertData and len(insertData) > 0:
            return ResponseModel(True, "Registered New User Successfully", insertData)
        else:
            return ResponseModel(False, "Unable to Registered New User")


# GET USER DETAILS
@app.get("/user/{userId}")
async def getUserById(userId: str):
    existUser = json.loads(dumps(userCollection.find({"_id": ObjectId(userId)})))
    if existUser and len(existUser) > 0:
        return ResponseModel(True, "User Details Found", existUser)
    else:
        return ResponseModel(False, "User Not Found")


# UPDATE USER DETAILS
@app.put("/user/{userId}")
async def getUserById(item: UpdateUser, userId: str):
    updatedData = userCollection.update_one(
        {"_id": ObjectId(userId)},
        {"$set": {"email": item.email, "name": item.name}},
    )
    if updatedData:
        return ResponseModel(True, "User Data updated successfully!!")
    else:
        return ResponseModel(False, "Unable to  Updated User Details")


# DELTE USER
@app.delete("/user/{userId}")
async def getUserById(userId: str):
    deleted = userCollection.delete_one(
        {"_id": ObjectId(userId)},
    )
    if deleted:
        return ResponseModel(True, "User Data Deleted successfully!!")
    else:
        return ResponseModel(False, "Unable to delete User")
