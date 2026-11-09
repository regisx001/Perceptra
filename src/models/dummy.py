from datetime import datetime, timezone
from src.extensions import db


class Dummy(db.Model):
    __tablename__ = "dummy"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<Dummy id={self.id} name={self.name}>"
