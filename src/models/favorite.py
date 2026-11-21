import uuid
from datetime import datetime, timezone
from src.extensions import db


class FavoriteImage(db.Model):
    __tablename__ = "favorite_images"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = db.Column(db.String(36), db.ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user = db.relationship("User", backref=db.backref("favorite_images", lazy=True, cascade="all, delete-orphan"))
    image = db.relationship("Image", backref=db.backref("favorited_by", lazy=True, cascade="all, delete-orphan"))

    __table_args__ = (
        db.UniqueConstraint("user_id", "image_id", name="uq_user_favorite_image"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_id": self.image_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
