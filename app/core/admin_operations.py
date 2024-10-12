from datetime import timedelta
from app.auth import create_access_token, get_password_hash, verify_password
from app.database import users_collection, assignments_collection
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserCreateResponse, UserLogin, UserLoginResponse, UserAssignmentUploadResponse, AdminListResponse
from app.schemas.assignment_schema import AssignmentUpdate, AssignmentListResponse
from fastapi import HTTPException, status
from bson import ObjectId, errors
from fastapi import HTTPException
from pymongo.errors import PyMongoError


async def register_admin(admin: UserCreate) -> UserCreateResponse:
    try:
        existing_admin = await users_collection.find_one({"username": admin.username})
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

        # Create a new admin document
        new_admin = {
            "username": admin.username,
            "password": get_password_hash(admin.password),
            "role": "admin"
        }
        result = await users_collection.insert_one(new_admin)
        return {"id": str(result.inserted_id), "message": "Admin registered successfully"}

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error") from e


async def login_admin(admin: UserLogin) -> UserLoginResponse:
    try:
        found_admin = await users_collection.find_one({"username": admin.username, "role": "admin"})
        # Hashed password check
        if not found_admin or not verify_password(admin.password, found_admin["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        access_token = create_access_token(
            data={"sub": found_admin["username"]}, expires_delta=timedelta(minutes=30))

        return {"id": str(found_admin["_id"]), "username": found_admin["username"], "access_token": access_token, "token_type": "bearer"}

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error") from e


async def get_assignments_for_admin(current_user: User, admin: str = None) -> AssignmentListResponse:
    try:
        if not current_user["role"] == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorised Admin")
        if admin:
            assignments = await assignments_collection.find({"admin": admin}).to_list(length=100)
        else:
            assignments = await assignments_collection.find({"admin_id": current_user["_id"]}).to_list(length=100)
        return {"assignments": [{"id": str(a["_id"]), "userId": a["userId"], "task": a["task"], "admin": a["admin"], "status": a["status"], "timestamp": a["timestamp"]} for a in assignments]}

    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Admin ID.")

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error") from e


async def update_assignment_status(assignment: AssignmentUpdate, current_user: User) -> dict:
    try:
        # Update status (accept/reject)
        if not current_user["role"] == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorised to accept assignments.")
        object_id = ObjectId(assignment.assignment_id)

        result = await assignments_collection.update_one(
            {"_id": ObjectId(object_id)},
            {"$set": {"status": assignment.status}}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")

        return {"message": "Status updated successfully"}

    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid assignment ID.")

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error") from e