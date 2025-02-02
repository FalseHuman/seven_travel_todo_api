from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from starlette import status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.users import User
from .auth import get_current_user


router = APIRouter(prefix='/permission', tags=['permission'])


@router.patch('/')
async def user_permission(db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)],
                          is_active: bool, is_admin: bool, user_id: int = None):
    if get_user.get('is_admin'):
        user = await db.scalar(select(User).where(User.id == user_id))
        model = User

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        else:
            await db.execute(update(model).where(model.id == user_id).values(is_active=is_active, is_admin=is_admin))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'User update'
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permission"
        )