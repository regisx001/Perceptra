import uuid
from datetime import datetime, timezone
from src.extensions import db


class RetrievalQuery(db.Model):
    __tablename__ = "retrieval_queries"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query_image_id = db.Column(db.String(36), db.ForeignKey("images.id", ondelete="SET NULL"), nullable=True, index=True)
    query_storage_key = db.Column(db.String(500), nullable=True)
    query_source = db.Column(db.String(20), nullable=False, default="upload")  # 'upload' or 'gallery'
    search_scope = db.Column(db.String(30), nullable=False, default="all")     # 'all', 'ghim10k', 'my_images', 'dataset', 'personal'
    configuration = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="completed")     # 'completed', 'failed', 'running'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship("User", backref=db.backref("retrieval_queries", lazy=True, cascade="all, delete-orphan"))
    query_image = db.relationship("Image", foreign_keys=[query_image_id], backref=db.backref("as_query_searches", lazy=True))
    iterations = db.relationship("RetrievalIteration", backref="retrieval_query", lazy=True, cascade="all, delete-orphan", order_by="RetrievalIteration.iteration_number")

    def to_dict(self, include_iterations: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "query_image_id": self.query_image_id,
            "query_storage_key": self.query_storage_key,
            "query_source": self.query_source,
            "search_scope": self.search_scope,
            "configuration": self.configuration,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "iterations_count": len(self.iterations) if self.iterations else 0,
        }
        if include_iterations:
            data["iterations"] = [it.to_dict(include_results=True, include_feedback=True) for it in self.iterations]
        return data


class RetrievalIteration(db.Model):
    __tablename__ = "retrieval_iterations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = db.Column(db.String(36), db.ForeignKey("retrieval_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    iteration_number = db.Column(db.Integer, nullable=False, default=0)
    retrieval_method = db.Column(db.String(30), nullable=False, default="initial")  # 'initial' or 'fre'
    feature_weights = db.Column(db.JSON, nullable=True)
    updated_query_vector = db.Column(db.JSON, nullable=True)
    feedback_count = db.Column(db.Integer, nullable=False, default=0)
    execution_time_ms = db.Column(db.Integer, nullable=False, default=0)
    total_candidates = db.Column(db.Integer, nullable=False, default=0)
    results_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    results = db.relationship("RetrievalResult", backref="iteration", lazy=True, cascade="all, delete-orphan", order_by="RetrievalResult.rank")
    feedbacks = db.relationship("RelevanceFeedback", backref="iteration", lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("query_id", "iteration_number", name="uq_retrieval_iteration_query_number"),
    )

    def to_dict(self, include_results: bool = False, include_feedback: bool = False) -> dict:
        data = {
            "id": self.id,
            "query_id": self.query_id,
            "iteration_number": self.iteration_number,
            "retrieval_method": self.retrieval_method,
            "feature_weights": self.feature_weights,
            "feedback_count": self.feedback_count,
            "execution_time_ms": self.execution_time_ms,
            "total_candidates": self.total_candidates,
            "results_count": self.results_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_results:
            data["results"] = [r.to_dict() for r in self.results]
        if include_feedback:
            data["feedback"] = [f.to_dict() for f in self.feedbacks]
        return data


class RetrievalResult(db.Model):
    __tablename__ = "retrieval_results"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    iteration_id = db.Column(db.String(36), db.ForeignKey("retrieval_iterations.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = db.Column(db.String(36), db.ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    rank = db.Column(db.Integer, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    feature_scores = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    image = db.relationship("Image", foreign_keys=[image_id])

    __table_args__ = (
        db.UniqueConstraint("iteration_id", "image_id", name="uq_retrieval_result_iter_image"),
        db.UniqueConstraint("iteration_id", "rank", name="uq_retrieval_result_iter_rank"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "iteration_id": self.iteration_id,
            "image_id": self.image_id,
            "rank": self.rank,
            "similarity_score": self.similarity_score,
            "feature_scores": self.feature_scores,
            "image": {
                "id": self.image.id,
                "filename": self.image.filename,
                "category_id": self.image.category_id,
                "category_name": self.image.category.name if self.image.category else "Uncategorized",
                "width": self.image.width,
                "height": self.image.height,
                "file_size": self.image.file_size,
                "source_type": self.image.source_type,
            } if self.image else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class RelevanceFeedback(db.Model):
    __tablename__ = "relevance_feedback"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    iteration_id = db.Column(db.String(36), db.ForeignKey("retrieval_iterations.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = db.Column(db.String(36), db.ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    judgment = db.Column(db.String(20), nullable=False)  # 'relevant' or 'irrelevant'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    image = db.relationship("Image", foreign_keys=[image_id])

    __table_args__ = (
        db.UniqueConstraint("iteration_id", "image_id", name="uq_relevance_feedback_iter_image"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "iteration_id": self.iteration_id,
            "image_id": self.image_id,
            "judgment": self.judgment,
            "image": {
                "id": self.image.id,
                "filename": self.image.filename,
                "category_name": self.image.category.name if self.image and self.image.category else "Uncategorized",
            } if self.image else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
