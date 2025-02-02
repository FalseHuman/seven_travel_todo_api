from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from typing import Optional

from app.schemas import CreateTask
from app.backend.db_depends import get_db
from app.models.tasks import Task
from sqlalchemy import select, update, insert, delete
from app.routers.auth import get_current_user

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def post_task(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)], create_task: CreateTask):
    await db.execute(insert(Task).values(title=create_task.title, description=create_task.description, status=create_task.status, user_id=int(user.get("id"))))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Task create is successful'
    }


@router.get('/')
async def all_tasks(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)], todo_status: Optional[str] = Query(None, enum=["todo", "in_progress", "done"])):
    tasks = await db.scalars(select(Task).where(Task.user_id == user.get("id"), Task.status == todo_status)) if todo_status is not None else await db.scalars(select(Task).where(Task.user_id == user.get("id")))
    if tasks is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'There are not tasks with status {todo_status}'
        )
    return tasks.all()


@router.get('/{task_id}')
async def get_task(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)], task_id: int):
    task = await db.scalar(select(Task).where(Task.user_id == user.get("id"), Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no task found'
        )
    return task


@router.put('/{task_id}')
async def put_task(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)], task_id: int, update_task: CreateTask):
    task = await db.scalar(select(Task).where(Task.user_id == user.get("id"), Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no task found'
        )
    else:
        await db.execute(update(Task).where(Task.user_id == user.get("id"),  Task.id == task_id).values(title=update_task.title, description=update_task.description, status=update_task.status))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Task update is successful'
        }


@router.delete('/{task_id}')
async def put_task(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)], task_id: int):
    task = await db.scalar(select(Task).where(Task.user_id == user.get("id"), Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no task found'
        )
    else:
        await db.execute(delete(Task).where(Task.user_id == user.get("id"),  Task.id == task_id))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Task delete is successful'
        }
