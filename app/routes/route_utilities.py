from datetime import datetime

from flask import Response, abort, make_response, request

from ..db import db


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except ValueError:
        response = {"details": f"{cls.__name__.lower()} {model_id} invalid"}
        abort(make_response(response, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if not model:
        response = {"details": f"{cls.__name__.lower()} {model_id} not found"}
        abort(make_response(response, 404))

    return model


def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201


def get_models_with_filters(cls):
    query = db.select(cls)

    sort_param = request.args.get("sort", "").lower()

    match sort_param:
        case "asc":
            query = query.order_by(cls.title.asc(), cls.id)
        case "desc":
            query = query.order_by(cls.title.desc(), cls.id)
        case _:
            query = query.order_by(cls.id)

    models = db.session.scalars(query)
    models_response = [model.to_dict() for model in models]

    return models_response, 200

def completed_at_parser(value):
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        abort(make_response({"details": "Invalid date"}, 400))

def delete_model(cls, model_id):
    model = validate_model(cls, model_id)
    db.session.delete(model)
    db.session.commit()

    return Response(status=204, mimetype="application/json")