from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from app.auth import decode_access_token
from app.database import users_collection
from app.models.token import TokenData
from app.models.user import User
from pymongo.errors import PyMongoError
from typing import Annotated


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if not payload:
            raise credentials_exception

        username: str = payload.get("sub")
        token_data = TokenData(username=username)

        user = await users_collection.find_one({"username": token_data.username})
        if not user:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    except PyMongoError as e:
        raise HTTPException(
            status_code=500, detail="Database error occurred while fetching user data") from e

    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user