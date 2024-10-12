from typing import Annotated
from fastapi import APIRouter, Depends
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.assignment_schema import AssignmentListResponse, AssignmentUpdate, AssignmentUpdateResponse
from app.services.admin_service import register_admin, login_admin, get_assignments_for_admin, update_assignment_status
from app.schemas.user_schema import UserCreate, UserCreateResponse, UserLogin, UserLoginResponse

router = APIRouter()


@router.post("/register", response_model=UserCreateResponse, summary="Register a new admin")
async def register_admin_endpoint(admin: UserCreate):
    result = await register_admin(admin)
    return result


@router.post("/login", response_model=UserLoginResponse, summary="Admin Login")
async def login_admin_endpoint(admin: Annotated[UserLogin, Depends()]):
    admin_data = await login_admin(admin)
    return admin_data


@router.get("/assignments", response_model=AssignmentListResponse, summary="Get all assignments")
async def get_assignments_endpoint(current_user: Annotated[User, Depends(get_current_active_user)], admin: str | None = None):
    assignments = await get_assignments_for_admin(current_user, admin)
    return assignments


@router.post("/assignments/{id}/accept", response_model=AssignmentUpdateResponse, summary="Accept an assignment")
async def accept_assignment_endpoint(id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    result = await update_assignment_status(AssignmentUpdate(assignment_id=id, status="accepted"), current_user)
    return result


@router.post("/assignments/{id}/reject", response_model=AssignmentUpdateResponse, summary="Reject an assignment")
async def reject_assignment_endpoint(id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    result = await update_assignment_status(AssignmentUpdate(assignment_id=id, status="rejected"), current_user)
    return result