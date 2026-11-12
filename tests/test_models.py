import pytest
from sqlalchemy.exc import IntegrityError
from src.models import Dummy, User, Category, Image, ImageFeature


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


def test_category_hierarchy_and_relationships(db_session):
    user = User(email="catuser@example.com")
    user.set_password("pass123")
    db_session.add(user)
    db_session.commit()

    parent_cat = Category(user_id=user.id, name="Nature")
    db_session.add(parent_cat)
    db_session.commit()

    sub_cat = Category(user_id=user.id, parent_id=parent_cat.id, name="Landscapes")
    db_session.add(sub_cat)
    db_session.commit()

    assert sub_cat.parent.name == "Nature"
    assert len(parent_cat.subcategories) == 1
    assert parent_cat.subcategories[0].name == "Landscapes"
    assert sub_cat.to_dict()["parent_id"] == parent_cat.id
    assert len(sub_cat.id) == 36
    assert len(parent_cat.id) == 36


def test_image_creation_and_derived_images(db_session):
    user = User(email="imguser@example.com")
    user.set_password("pass123")
    db_session.add(user)
    db_session.commit()

    category = Category(user_id=user.id, name="Animals")
    db_session.add(category)
    db_session.commit()

    original_image = Image(
        owner_id=user.id,
        category_id=category.id,
        filename="dog.jpg",
        storage_key="uploads/dog_abc123.jpg",
        source_type="upload",
        mime_type="image/jpeg",
        file_size=10240,
        width=800,
        height=600,
        checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    db_session.add(original_image)
    db_session.commit()

    derived_image = Image(
        owner_id=user.id,
        category_id=category.id,
        parent_image_id=original_image.id,
        filename="dog_crop.jpg",
        storage_key="derived/dog_crop_def456.jpg",
        source_type="derived",
        mime_type="image/jpeg",
        file_size=5120,
        width=400,
        height=300,
        checksum="d3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b856",
        transformation_params={"action": "crop", "box": [0, 0, 400, 300]},
    )
    db_session.add(derived_image)
    db_session.commit()

    assert derived_image.parent_image.filename == "dog.jpg"
    assert len(original_image.derived_images) == 1
    assert original_image.derived_images[0].transformation_params["action"] == "crop"


def test_image_feature_and_unique_constraint(db_session):
    dataset_image = Image(
        owner_id=None,
        category_id=None,
        filename="ghim_001.jpg",
        storage_key="dataset/ghim_001.jpg",
        source_type="dataset",
        mime_type="image/jpeg",
        file_size=20480,
        width=1024,
        height=768,
        checksum="13b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b857",
    )
    db_session.add(dataset_image)
    db_session.commit()

    feature1 = ImageFeature(
        image_id=dataset_image.id,
        feature_type="color_histogram",
        extractor_version="v1.0",
        feature_values=[0.1, 0.4, 0.5],
        parameters={"bins": 32, "color_space": "HSV"},
    )
    db_session.add(feature1)
    db_session.commit()

    assert len(dataset_image.features) == 1
    assert dataset_image.features[0].feature_type == "color_histogram"

    # Attempt to insert duplicate (image_id, feature_type, extractor_version)
    duplicate_feature = ImageFeature(
        image_id=dataset_image.id,
        feature_type="color_histogram",
        extractor_version="v1.0",
        feature_values=[0.2, 0.3, 0.5],
    )
    db_session.add(duplicate_feature)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
