from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import PositiveInt
from sqlalchemy import delete, or_, select
from sqlalchemy.exc import SQLAlchemyError

from db import models
from db.session import DBSession
from service.core.celery_app import celery_app
from service.core.dependencies import (get_current_manager, get_current_user,
                                       get_session)
from service.schemas import v1 as schemas_v1

router = APIRouter()


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas_v1.TaskResponse
)
async def create_task(
    input_data: schemas_v1.CreateTask,
    session: DBSession = Depends(get_session),
    current_manager: models.User = Depends(get_current_manager),
) -> models.Task:
    """
    Create Task by Manager\n
    Create Task by Manager. Return Task\n
    Responses:\n
    `201` CREATED - Everything is good (SUCCESS Response)\n
    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    user_query = select(models.User).where(
        models.User.id == input_data.responsible_person_id
    )
    with session() as db:
        user = db.execute(user_query).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )
    task = models.Task(
        name=input_data.name,
        description=input_data.description,
        responsible_person_id=input_data.responsible_person_id,
        status=input_data.status.value,
        priority=input_data.priority.value,
        created_by=current_manager.id,
    )
    with session() as db:
        db.add(task)
        db.commit()
        db.refresh(task)

    celery_app.send_task(
        "service.tasks.delay.task_creation_confirm",
        args=[user.email, task.name],
    )
    return task


@router.put("/{task_id}", response_model=schemas_v1.TaskResponse)
async def update_task(
    task_id: PositiveInt,
    input_data: schemas_v1.CreateTask,
    session: DBSession = Depends(get_session),
    current_manager: models.User = Depends(get_current_manager),
) -> models.Task:
    """
    Update Task by Manager\n
    Update Task by Manager. Return Task\n
    Responses:\n
    `201` OK - Everything is good (SUCCESS Response)\n
    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    task_query = select(models.Task).where(models.Task.id == task_id)
    with session() as db:
        task = db.execute(task_query).scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist"
        )
    user_query = select(models.User).where(
        models.User.id == input_data.responsible_person_id
    )
    with session() as db:
        user = db.execute(user_query).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    task.name = (input_data.name,)
    task.description = (input_data.description,)
    task.responsible_person_id = (input_data.responsible_person_id,)
    task.status = (input_data.status.value,)
    task.priority = (input_data.priority.value,)

    with session() as db:
        db.add(task)
        db.commit()
        db.refresh(task)
    celery_app.send_task(
        "service.tasks.delay.task_creation_confirm",
        args=[user.email, task.name],
    )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: PositiveInt,
    session: DBSession = Depends(get_session),
    current_manager: models.User = Depends(get_current_manager),
) -> None:
    """
    Delete Task by Manager\n
    Delete Task by Manager. Return\n
    Responses:\n
    `204` NO_CONTENT- DELETE Instance (SUCCESS Response)\n
    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    delete_query = delete(models.Task).where(
        models.Task.id == task_id,
    )
    with session() as db:
        db.execute(delete_query)
        db.commit()

    return


@router.get("/", response_model=Page[schemas_v1.TaskResponse])
async def get_tasks(
    session: DBSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
) -> models.Task:
    """
    Get all tasks\n
    Update Task by Manager. Return Task\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    tasks_query = select(models.Task)

    with session() as db:
        return paginate(db, tasks_query)


@router.get("/me/", response_model=Page[schemas_v1.TaskResponse])
async def get_my_tasks(
    session: DBSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
) -> models.Task:
    """
    Get my tasks\n
    Get my tasks. Return Task\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    assign_task_ids_query = (
        select(models.TaskExecutors.task_id)
        .where(models.TaskExecutors.user_id == user.id)
        .subquery()
    )

    tasks_query = select(models.Task).where(
        or_(
            models.Task.responsible_person_id == user.id,
            models.Task.id.in_(assign_task_ids_query),
        )
    )

    with session() as db:
        return paginate(db, tasks_query)


@router.get("/{task_id}/", response_model=schemas_v1.TaskResponse)
async def get_task_by_id(
    task_id: PositiveInt,
    session: DBSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
) -> models.Task:
    """
    Get task by id\n
    Get task by id. Return Task\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n

    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    task_query = select(models.Task).where(models.Task.id == task_id)
    with session() as db:
        task = db.execute(task_query).scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist"
        )
    return task


@router.post("/{task_id}/user/{user_id}", response_model=schemas_v1.AssignResponse)
async def assign_user_to_task(
    task_id: PositiveInt,
    user_id: PositiveInt,
    session: DBSession = Depends(get_session),
    current_manager: models.User = Depends(get_current_manager),
):
    """
    Assign User to task\n
    Assign User to task. Return  Task with assign Users\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `400` BAD_REQUEST - Invalid request data\n
    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    task_executors_instance = models.TaskExecutors(user_id=user_id, task_id=task_id)
    try:
        with session() as db:
            db.add(task_executors_instance)
            db.commit()
            db.refresh(task_executors_instance)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request data"
        )

    celery_app.send_task(
        "service.tasks.delay.task_assign_confirm",
        args=[
            task_executors_instance.assigned_user.email,
            task_executors_instance.task.name,
        ],
    )

    return task_executors_instance


@router.delete("/{task_id}/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_user_from_task(
    task_id: PositiveInt,
    user_id: PositiveInt,
    session: DBSession = Depends(get_session),
    current_manager: models.User = Depends(get_current_manager),
):
    """
    Unassign User to task\n
    Unassign User to task. Return  Task with assign Users\n
    Responses:\n
    `204` NO_CONTENT- DELETE Instance (SUCCESS Response)\n
    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    user_email_query = select(models.User.email).where(models.User.id == user_id)
    with session() as db:
        email = db.execute(user_email_query).scalar_one_or_none()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User  not found"
        )
    task_name_query = select(models.Task.name).where(models.Task.id == task_id)
    with session() as db:
        name = db.execute(task_name_query).scalar_one_or_none()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task  not found"
        )

    delete_query = delete(models.TaskExecutors).where(
        models.TaskExecutors.task_id == task_id, models.TaskExecutors.user_id == user_id
    )

    with session() as db:
        db.execute(delete_query)
        db.commit()

    celery_app.send_task(
        "service.tasks.delay.task_unassign_confirm",
        args=[email, name],
    )

    return


@router.get("/{task_id}/assigners", response_model=Page[schemas_v1.User])
async def get_task_assigners(
    task_id: PositiveInt,
    session: DBSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
) -> models.Task:
    """
    Get task assigners\n
    Get task assigners. Return Task\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n

    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    task_query = select(models.Task).where(models.Task.id == task_id)
    with session() as db:
        task = db.execute(task_query).scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist"
        )
    assigners_query = (
        select(models.User)
        .join(models.TaskExecutors, models.User.id == models.TaskExecutors.user_id)
        .where(models.TaskExecutors.task_id == task_id)
    )
    with session() as db:
        return paginate(db, assigners_query)
