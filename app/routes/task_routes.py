import os
from datetime import datetime

from flask import Blueprint, Response, abort, current_app, make_response, request
import requests
from .route_utilities import validate_model

from app.models.task import Task

from ..db import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
slack_url = "https://slack.com/api/chat.postMessage"
token = os.environ.get('SLACKBOT_TOKEN')
channel = os.environ.get('SLACKBOT_CHANNEL')


@tasks_bp.post("")
def create_task():
    try:
        task = Task.from_dict(request.get_json())
    except KeyError:
        return {"details": "Invalid data"}, 400

    db.session.add(task)
    db.session.commit()

    return task.to_dict(), 201

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
    return validate_model(Task, task_id).to_dict()


@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()
    return Response(status=204, mimetype="application/json")


@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now()
    db.session.commit()
    headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json",
    }

    request_body = {"channel": channel, "text": f"Someone just completed the task {task.title}"}
    try:
        response = requests.post(slack_url, json=request_body, headers=headers)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            current_app.logger.error(f"Slack notification failed: {data.get('error')}")
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Slack request failed: {e}")
    except ValueError:
        current_app.logger.error("Slack returned invalid JSON")

    
    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)
    
    task.completed_at = None
    db.session.commit()
    return Response(status=204, mimetype="application/json")