from flask import Blueprint, Response, abort, current_app, make_response, request
import requests

from app.models.task import Task
from .route_utilities import validate_model, create_model_with_response

from app.models.goal import Goal

from ..db import db

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@bp.post("")
def create_goal():
    return create_model_with_response(Goal, request.get_json())


@bp.get("")
def get_all_goals():
    query = db.select(Goal)

    sort_param = request.args.get("sort", "").lower()

    match sort_param:
        case "asc":
            query = query.order_by(Goal.title.asc(), Goal.id)
        case "desc":
            query = query.order_by(Goal.title.desc(), Goal.id)
        case _:
            query = query.order_by(Goal.id)

    goals = db.session.scalars(query)

    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_dict())

    return goals_response, 200


@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    return validate_model(Goal, goal_id).to_dict()


@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()
    return Response(status=204, mimetype="application/json")


@bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.post("/<goal_id>/tasks")
def add_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    tasks = [validate_model(Task, task_id) for task_id in request_body["task_ids"]]

    goal.tasks = tasks
    db.session.commit()

    tasks_ids = [task.id for task in goal.tasks]

    return {"id": goal.id, "task_ids": tasks_ids}, 200


@bp.get("/<goal_id>/tasks")
def get_all_tasks_with_same_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    tasks = [task.to_dict() for task in goal.tasks]
    return {"id": goal.id, "title": goal.title, "tasks": tasks}
