from typing import Annotated
from fastapi import APIRouter, Depends
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.assignment_schema import AssignmentCreate
from app.services.user_service import register_user, login_user, upload_assignment, get_admins
from app.schemas.user_schema import AdminListResponse, UserAssignmentUploadResponse, UserCreate, UserCreateResponse, UserLogin, UserLoginResponse

router = APIRouter()


@router.post("/register", response_model=UserCreateResponse, summary="Register a new user")
async def register_user_endpoint(user: UserCreate):
    result = await register_user(user)
    return result


@router.post("/login", response_model=UserLoginResponse, summary="User Login")
async def login_user_endpoint(user: Annotated[UserLogin, Depends()]):
    user_data = await login_user(user)
    return user_data


@router.post("/upload", response_model=UserAssignmentUploadResponse, summary="Upload a new assignment")
async def upload_assignment_endpoint(assignment: AssignmentCreate, current_user: Annotated[User, Depends(get_current_active_user)]):
    result = await upload_assignment(assignment, current_user)
    return result


@router.get("/admins", response_model=AdminListResponse, summary="Fetch all admins")
async def get_admins_endpoint(current_user: Annotated[User, Depends(get_current_active_user)]):
    result = await get_admins()
    return result