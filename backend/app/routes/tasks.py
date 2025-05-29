from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import logging

from ..models import (
    TaskCreateNLP, TaskCreateStructured, TaskUpdate, 
    TaskResponse, APIResponse, Priority
)
from app.database import get_task_repository, TaskRepository
from ..gemini_service import gemini_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def convert_task_to_response(task_dict: dict) -> TaskResponse:
    """Convert database task dict to TaskResponse model"""
    return TaskResponse(
        id=str(task_dict["_id"]),
        task_name=task_dict["task_name"],
        assignee=task_dict.get("assignee"),
        due_date_time=task_dict.get("due_date_time"),
        priority=Priority(task_dict.get("priority", "P3")),
        original_text=task_dict.get("original_text"),
        created_at=task_dict["created_at"],
        updated_at=task_dict["updated_at"]
    )


@router.post("/parse", response_model=APIResponse)
async def parse_and_create_task(
    task_input: TaskCreateNLP,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Parse natural language task input and create a new task"""
    try:
        # Parse the natural language input using Gemini
        
        gemini_response = await gemini_service.parse_task(task_input.text)

        if not gemini_response:
            raise HTTPException(
                status_code=400, 
                detail="Failed to parse the task. Please try rephrasing your input."
            )
        
        # Convert Gemini response to structured task data
        due_date_time = None
        if gemini_response.due_date_time:
            due_date_time = gemini_service.parse_datetime(gemini_response.due_date_time)
        
        priority = gemini_service.parse_priority(gemini_response.priority_hint)
        
        # Create structured task data
        task_data = {
            "task_name": gemini_response.task_name,
            "assignee": gemini_response.assignee,
            "due_date_time": due_date_time,
            "priority": priority.value,
            "original_text": task_input.text,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save to database
        created_task = await task_repo.create_task(task_data)
        task_response = convert_task_to_response(created_task)
        
        return APIResponse(
            success=True,
            message="Task created successfully",
            data=task_response.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks(task_repo: TaskRepository = Depends(get_task_repository)):
    """Get all tasks"""
    try:
        tasks = await task_repo.get_all_tasks()
        return [convert_task_to_response(task) for task in tasks]
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Get a specific task by ID"""
    try:
        task = await task_repo.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return convert_task_to_response(task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{task_id}", response_model=APIResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Update a task"""
    try:
        # Check if task exists
        existing_task = await task_repo.get_task_by_id(task_id)
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Prepare update data (only include non-None fields)
        update_data = {}
        if task_update.task_name is not None:
            update_data["task_name"] = task_update.task_name
        if task_update.assignee is not None:
            update_data["assignee"] = task_update.assignee
        if task_update.due_date_time is not None:
            update_data["due_date_time"] = task_update.due_date_time
        if task_update.priority is not None:
            update_data["priority"] = task_update.priority.value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update the task
        updated_task = await task_repo.update_task(task_id, update_data)
        if not updated_task:
            raise HTTPException(status_code=500, detail="Failed to update task")
        
        task_response = convert_task_to_response(updated_task)
        
        return APIResponse(
            success=True,
            message="Task updated successfully",
            data=task_response.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{task_id}", response_model=APIResponse)
async def delete_task(
    task_id: str,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Delete a task"""
    try:
        # Check if task exists
        existing_task = await task_repo.get_task_by_id(task_id)
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Delete the task
        deleted = await task_repo.delete_task(task_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete task")
        
        return APIResponse(
            success=True,
            message="Task deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
