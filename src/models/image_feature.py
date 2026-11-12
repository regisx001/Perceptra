import uuid
from datetime import datetime, timezone
from src.extensions import db


class ImageFeature(db.Model):
    __tablename__ = "image_features"
    __table_args__ = (
        db.UniqueConstraint(
            "image_id",
            "feature_type",
            "extractor_version",
            name="uq_image_feature_type_version",
        ),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_id = db.Column(db.String(36), db.ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_type = db.Column(db.String(50), nullable=False, index=True)
    extractor_version = db.Column(db.String(50), nullable=False)
    feature_values = db.Column(db.JSON, nullable=False)
    parameters = db.Column(db.JSON, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    image = db.relationship("Image", backref=db.backref("features", lazy=True, cascade="all, delete-orphan"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "image_id": self.image_id,
            "feature_type": self.feature_type,
            "extractor_version": self.extractor_version,
            "feature_values": self.feature_values,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<ImageFeature id={self.id} image_id={self.image_id} feature_type='{self.feature_type}' version='{self.extractor_version}'>"
