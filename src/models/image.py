import uuid
from datetime import datetime, timezone
from src.extensions import db


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = db.Column(db.String(36), db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_image_id = db.Column(db.String(36), db.ForeignKey("images.id", ondelete="SET NULL"), nullable=True, index=True)
    filename = db.Column(db.String(255), nullable=False)
    storage_key = db.Column(db.String(500), unique=True, nullable=False, index=True)
    source_type = db.Column(db.String(20), nullable=False, default="dataset")  # 'dataset', 'upload', 'derived'
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    checksum = db.Column(db.String(64), nullable=False, index=True)
    transformation_params = db.Column(db.JSON, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    owner = db.relationship("User", backref=db.backref("images", lazy=True))
    category = db.relationship("Category", backref=db.backref("images", lazy=True))
    parent_image = db.relationship("Image", remote_side=[id], backref=db.backref("derived_images", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "category_id": self.category_id,
            "parent_image_id": self.parent_image_id,
            "filename": self.filename,
            "storage_key": self.storage_key,
            "source_type": self.source_type,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
            "checksum": self.checksum,
            "transformation_params": self.transformation_params,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Image id={self.id} filename='{self.filename}' source_type='{self.source_type}'>"
