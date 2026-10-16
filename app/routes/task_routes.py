from datetime import datetime

from flask import Blueprint, Response, abort, make_response, request

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
        return {"details": "Invalid data"}, 400


@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)

    sort_param = request.args.get("sort", "").lower()

    match sort_param:
        case "asc":
            query = query.order_by(Task.title.asc(), Task.id)
        case "desc":
            query = query.order_by(Task.title.desc(), Task.id)
        case _:
            query = query.order_by(Task.id)

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
    request_body = request.get_json()

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

@tasks_bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_task(task_id)

    task.completed_at = datetime.now()
    db.session.commit()
    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_task(task_id)
    
    task.completed_at = None
    db.session.commit()
    return Response(status=204, mimetype="application/json")