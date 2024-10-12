from datetime import datetime, timedelta
from app.auth import create_access_token, get_password_hash, verify_password
from app.database import users_collection, assignments_collection
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserCreateResponse, UserLogin, UserLoginResponse, UserAssignmentUploadResponse, AdminListResponse
from app.schemas.assignment_schema import AssignmentCreate
from fastapi import HTTPException, status
from bson import ObjectId, errors
from pymongo.errors import PyMongoError


async def register_user(user: UserCreate) -> UserCreateResponse:
    try:
        existing_user = await users_collection.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

        # Create a new user document
        new_user = {
            "username": user.username,
            "password": get_password_hash(user.password),
            "role": "user"
        }
        result = await users_collection.insert_one(new_user)
        return {"id": str(result.inserted_id), "message": "User registered successfully"}

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error") from e


async def login_user(user: UserLogin) -> UserLoginResponse:
    try:
        found_user = await users_collection.find_one({"username": user.username})

        if not found_user or not verify_password(user.password, found_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        access_token = create_access_token(
            data={"sub": found_user["username"]}, expires_delta=timedelta(minutes=30))

        return {"id": str(found_user["_id"]), "username": found_user["username"], "access_token": access_token, "token_type": "bearer"}

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error") from e


async def upload_assignment(assignment: AssignmentCreate, current_user: User) -> UserAssignmentUploadResponse:
    try:
        # Create a new assignment document
        admin = await users_collection.find_one({"username": assignment.admin})

        if not admin or not admin["role"] == "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Admin '{assignment.admin}' not found.")

        new_assignment = {
            "user_id": current_user["_id"],
            "userId": assignment.userId,
            "task": assignment.task,
            "admin_id": admin["_id"],
            "admin": assignment.admin,
            "status": "pending",
            "timestamp": datetime.now()
        }
        result = await assignments_collection.insert_one(new_assignment)
        return {"id": str(result.inserted_id), "message": "Assignment uploaded successfully"}

    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Admin ID.")

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error") from e


async def get_admins() -> AdminListResponse:
    try:
        # Return all admins
        admins = await users_collection.find({"role": "admin"}).to_list(length=None)

        if not admins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No admins found.")

        admins_list = [
            {"id": str(admin["_id"]), "username": admin["username"]} for admin in admins]

        return {"admins": admins_list}

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error") from e