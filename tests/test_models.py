from src.models.dummy import Dummy


def test_dummy_model_creation(db_session):
    item = Dummy(name="test_item")
    db_session.add(item)
    db_session.commit()

    retrieved = Dummy.query.filter_by(name="test_item").first()
    assert retrieved is not None
    assert retrieved.id is not None
    assert retrieved.name == "test_item"
    assert retrieved.created_at is not None
    assert repr(retrieved) == f"<Dummy id={retrieved.id} name=test_item>"
