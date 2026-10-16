from flask import Blueprint, request, abort, make_response, Response
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

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task).order_by(Task.id)
    tasks = db.session.scalars(query)

    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())

    return tasks_response, 200

@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    return validate_task(task_id).to_dict()

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body= request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()
    return Response(status=204, mimetype="application/json")
    
@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except ValueError:
        abort(make_response({"details": f"task id {task_id} invalid"}, 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        abort(make_response({"details": f"task {task_id} not found"}, 404))
    return task