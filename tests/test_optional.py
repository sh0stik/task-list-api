from datetime import datetime

import pytest

from app.db import db
from app.models.task import Task

# Sort:

def test_get_tasks_with_invalid_sort_returns_default_order(client, three_tasks):
    response = client.get("/tasks?sort=hds")
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "id": 1,
            "title": "Water the garden 🌷",
            "description": "",
            "is_complete": False,
        },
        {
            "id": 2,
            "title": "Answer forgotten email 📧",
            "description": "",
            "is_complete": False,
        },
        {
            "id": 3,
            "title": "Pay my outstanding tickets 😭",
            "description": "",
            "is_complete": False,
        },
    ]


def test_get_tasks_with_uppercase_sort_desc(client, three_tasks):
    response = client.get("/tasks?sort=DESC")
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "id": 1,
            "title": "Water the garden 🌷",
            "description": "",
            "is_complete": False,
        },
        {
            "id": 3,
            "title": "Pay my outstanding tickets 😭",
            "description": "",
            "is_complete": False,
        },
        {
            "id": 2,
            "title": "Answer forgotten email 📧",
            "description": "",
            "is_complete": False,
        },
    ]


def test_get_tasks_with_empty_sort_param(client, three_tasks):
    response = client.get("/tasks?sort=")
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "id": 1,
            "title": "Water the garden 🌷",
            "description": "",
            "is_complete": False,
        },
        {
            "id": 2,
            "title": "Answer forgotten email 📧",
            "description": "",
            "is_complete": False,
        },
        {
            "id": 3,
            "title": "Pay my outstanding tickets 😭",
            "description": "",
            "is_complete": False,
        },
    ]


# Create:

def test_create_task_with_valid_completed_at(client):
    response = client.post(
        "/tasks",
        json={
            "title": "A completed task",
            "description": "Test",
            "completed_at": "2026-10-22T10:30:00",
        },
    )

    assert response.status_code == 201

    task = db.session.get(Task, 1)
    assert task.title == "A completed task"
    assert task.completed_at == datetime(2026, 10, 22, 10, 30, 0)


def test_create_task_with_none_completed_at(client):
    response = client.post(
            "/tasks",
            json={
                "title": "A completed task",
                "description": "Test",
                "completed_at": None,
            },
        )
    
    assert response.status_code == 201

    task = db.session.get(Task, 1)
    assert task.title == "A completed task"
    assert task.completed_at == None

def test_create_task_with_invalid_completed_at_string_returns_400(client):
    response = client.post(
            "/tasks",
            json={
                "title": "A completed task",
                "description": "Test",
                "completed_at": "datetime",
            },
        )
    
    assert response.status_code == 400

    response_body = response.get_json()
    
    assert "details" in response_body 
    assert response_body == {
                "details": "Invalid date"
            }
    tasks = db.session.scalars(db.select(Task)).all()
    assert tasks == []
    
def test_create_task_with_non_string_completed_at_returns_400(client):
    response = client.post(
            "/tasks",
            json={
                "title": "A completed task",
                "description": "Test",
                "completed_at": 12343456,
            },
        )
    
    assert response.status_code == 400

    response_body = response.get_json()
    
    assert "details" in response_body 
    assert response_body == {
                "details": "Invalid date"
            }
    tasks = db.session.scalars(db.select(Task)).all()
    assert tasks == []

# Update:

def test_update_task_with_valid_completed_at(client, one_task):
    response = client.put(
            "/tasks/1",
            json={
                "title": "Go on my daily walk 🏞",
                "description": "Notice something new every day",
                "completed_at": "2026-10-22T10:30:00",
            },
        )
    
    assert response.status_code == 204

    task = db.session.get(Task, 1)
    assert task.title == "Go on my daily walk 🏞"
    assert task.completed_at == datetime(2026, 10, 22, 10, 30, 0)

def test_update_task_with_invalid_completed_at_returns_400(client, one_task):
    response = client.put(
            "/tasks/1",
            json={
                "title": "Go on my daily walk 🏞",
                "description": "Notice something new every day",
                "completed_at": "datetime",
            },
        )
    
    assert response.status_code == 400
    
    response_body = response.get_json()
    
    assert "details" in response_body 
    assert response_body == {
                "details": "Invalid date"
            }

    task = db.session.get(Task, 1)
    assert task.title == "Go on my daily walk 🏞"
    assert task.completed_at == None

