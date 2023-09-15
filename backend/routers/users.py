from fastapi import APIRouter, Request, Body, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from models.user_model import UserBase, LoginBase, CurrentUser

from authentication import AuthHandler

from bson.objectid import ObjectId

user_router = APIRouter()

# instantiate the Auth Handler
auth_handler = AuthHandler()

# register user
# validate the data and create a user if the username and the email are valid
#  and available


@user_router.post("/register", response_description="Register user")
async def register(request: Request, newUser: UserBase = Body(...)) -> UserBase:
    user_dump = newUser.model_dump()

    # hash the password before inserting it into MongoDB
    newUser.password = auth_handler.get_password_hash(newUser.password)

    newUser = jsonable_encoder(newUser)
    email = user_dump["email"]
    username = user_dump['username']

    # check existing user or email 409 Conflict:
    if (
        await request.app.mongodb["users"].find_one({"email": email})
        is not None
    ):
        raise HTTPException(
            status_code=409, detail=f"User with email {email} already exists"
        )

    # check existing user or email 409 Conflict:
    if (
        await request.app.mongodb["users"].find_one({"username": username})
        is not None
    ):
        raise HTTPException(
            status_code=409,
            detail=f"User with username {username} already exists",
        )

    user = await request.app.mongodb["users"].insert_one(newUser)
    created_user = await request.app.mongodb["users"].find_one(
        {"_id": user.inserted_id}
    )

    return created_user


# post user
@user_router.post("/login", response_description="Login user")
async def login(request: Request, loginUser: LoginBase = Body(...)) -> JSONResponse:
    # find the user by email
    user = await request.app.mongodb["users"].find_one({"email": loginUser.email})

    # check password
    if (user is None) or (
        not auth_handler.verify_password(loginUser.password, user["password"])
    ):
        raise HTTPException(status_code=401, detail="Invalid email and/or password")

    token = auth_handler.encode_token(str(user["_id"]))
    response = JSONResponse(content={"token": token})

    return response


# me route
@user_router.get("/me", response_description="Logged in user data")
async def me(request: Request, userId=Depends(auth_handler.auth_wrapper)):

    o_id = ObjectId(userId)
    currentUser = await request.app.mongodb["users"].find_one({"_id": o_id})

    result = CurrentUser(**currentUser)
    result_dict = result.model_dump()
    result_dict["id"] = userId

    return result
