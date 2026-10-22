from app import create_app, db

from app.models.task import Task
from app.models.goal import Goal


my_app = create_app()
with my_app.app_context():
    db.create_all()
    goals = [
        Goal(title="Build a habit of going outside daily"),
        Goal(title="Get the apartment move-ready"),
        Goal(title="Finish the Task List API"),
    ]

    tasks = [
        Task(
            title="Go on my daily walk",
            description="Notice something new every day",
            completed_at=None,
            goal_id=1,
        ),
        Task(
            title="Water the garden",
            description="Front and back beds",
            completed_at="2026-10-20T08:15:00",
            goal_id=1,
        ),
        Task(
            title="Try a new hiking trail",
            description="Pick one within 30 minutes",
            completed_at=None,
            goal_id=1,
        ),
        Task(
            title="Pack the kitchen",
            description="Keep out one pot and one pan",
            completed_at=None,
            goal_id=2,
        ),
        Task(
            title="Schedule movers",
            description="Get at least two quotes",
            completed_at="2026-10-18T14:30:00",
            goal_id=2,
        ),
        Task(
            title="Finish wave 6",
            description="Goal and task relationship routes",
            completed_at=None,
            goal_id=3,
        ),
        Task(
            title="Write the README",
            description="Document every endpoint",
            completed_at=None,
            goal_id=3,
        ),
        Task(
            title="Answer forgotten email",
            description="",
            completed_at=None,
            goal_id=None,
        ),
        Task(
            title="Pay outstanding tickets",
            description="",
            completed_at="2026-10-15T10:00:00",
            goal_id=None,
        ),
    ]

    db.session.bulk_save_objects(goals)
    db.session.bulk_save_objects(tasks)
    db.session.commit()
