import os
from datetime import datetime

from flask import Blueprint, Response, abort, current_app, make_response, request
import requests
from .route_utilities import completed_at_parser, get_models_with_filters, validate_model, create_model

from app.models.task import Task

from ..db import db

bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
slack_url = "https://slack.com/api/chat.postMessage"
token = os.environ.get("SLACKBOT_TOKEN")
channel = os.environ.get("SLACKBOT_CHANNEL")


@bp.post("")
def create_task():
    request_body = request.get_json()
    if "completed_at" in request_body:
        request_body["completed_at"] = completed_at_parser(request_body["completed_at"])
    return create_model(Task, request_body)


@bp.get("")
def get_all_tasks():
    return get_models_with_filters(Task)


@bp.get("/<task_id>")
def get_one_task(task_id):
    return validate_model(Task, task_id).to_dict()


@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    if "completed_at" in request_body:
        task.completed_at = completed_at_parser(request_body["completed_at"])

    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()
    return Response(status=204, mimetype="application/json")


@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now()
    db.session.commit()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    request_body = {
        "channel": channel,
        "text": f"Someone just completed the task {task.title}",
    }
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


@bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    db.session.commit()
    return Response(status=204, mimetype="application/json")