from sqlalchemy.orm import Mapped, mapped_column
from ..db import db
from datetime import datetime

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    def to_dict(self):
        is_complete = False
        if self.completed_at is not None:
            is_complete = True
        return {
            "id" : self.id,
            "title" : self.title,
            "description" : self.description,
            "is_complete" : is_complete
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title = data["title"],
            description = data["description"],
            completed_at = None
        )
        

