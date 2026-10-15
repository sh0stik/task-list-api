from flask import Blueprint, request
from app.models.task import Task

from ..db import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    try:
        task = Task.from_dict(request.get_json())
        db.session.add(task)
        db.session.commit()

        return task.to_dict(), 201
    except KeyError:
        return { "details": "Invalid data"}, 400

