from pydantic import BaseModel


class AssignmentCreate(BaseModel):
    userId: str
    task: str
    admin: str


class AssignmentUpdate(BaseModel):
    assignment_id: str
    status: str


class AssignmentUpdateResponse(BaseModel):
    message: str


class AssignmentListResponse(BaseModel):
    assignments: list[Assignment] | None