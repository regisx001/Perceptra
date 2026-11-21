import uuid
from datetime import datetime, timezone
from src.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    parent_id = db.Column(db.String(36), db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = db.relationship("User", backref=db.backref("categories", lazy=True, cascade="all, delete-orphan"))
    parent = db.relationship("Category", remote_side=[id], backref=db.backref("subcategories", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Category id={self.id} name='{self.name}' user_id={self.user_id} parent_id={self.parent_id}>"
