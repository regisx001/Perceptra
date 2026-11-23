import uuid
from pathlib import Path
from PIL import Image as PILImage
from src.extensions import db
from src.models.category import Category
from src.models.image import Image
from src.models.image_feature import ImageFeature
from src.services.dataset_service import DatasetIngestionService


def create_dummy_image(path: Path, color=(200, 100, 50), size=(100, 100)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = PILImage.new("RGB", size, color=color)
    img.save(path, format="JPEG")


def test_remove_dataset(app, tmp_path):
    storage_root = tmp_path / "storage"
    service = DatasetIngestionService(storage_root=str(storage_root))

    # Create dummy dataset files
    ds_dir = tmp_path / "test_ds"
    create_dummy_image(ds_dir / "cats" / "cat1.jpg", color=(10, 20, 30))
    create_dummy_image(ds_dir / "dogs" / "dog1.jpg", color=(40, 50, 60))

    with app.app_context():
        # Ingest
        stats = service.ingest_dataset(
            folder_path=ds_dir,
            dataset_name="test_ds",
            batch_size=10,
            compute_features=True,
            skip_existing=False,
            create_parent_category=True,
            max_workers=1,
        )
        assert stats.ingested == 2
        assert Image.query.filter_by(source_type="dataset").count() == 2
        assert ImageFeature.query.count() > 0

        # Now test removal of specific dataset
        del_stats = service.remove_dataset(dataset_name="test_ds")
        assert del_stats["images_deleted"] == 2
        assert del_stats["features_deleted"] > 0
        assert del_stats["categories_deleted"] >= 2
        assert del_stats["files_removed"] is True

        # Check DB and disk
        assert Image.query.filter_by(source_type="dataset").count() == 0
        assert ImageFeature.query.count() == 0
        assert not (storage_root / "datasets" / "test_ds").exists()


def test_remove_all_datasets(app, tmp_path):
    storage_root = tmp_path / "storage"
    service = DatasetIngestionService(storage_root=str(storage_root))

    ds_dir1 = tmp_path / "ds1"
    create_dummy_image(ds_dir1 / "alpha" / "a.jpg", color=(100, 110, 120))
    ds_dir2 = tmp_path / "ds2"
    create_dummy_image(ds_dir2 / "beta" / "b.jpg", color=(150, 160, 170))

    with app.app_context():
        service.ingest_dataset(folder_path=ds_dir1, dataset_name="ds1", max_workers=1)
        service.ingest_dataset(folder_path=ds_dir2, dataset_name="ds2", max_workers=1)
        assert Image.query.filter_by(source_type="dataset").count() == 2

        del_stats = service.remove_dataset(remove_all=True)
        assert del_stats["images_deleted"] == 2
        assert del_stats["features_deleted"] > 0
        assert del_stats["files_removed"] is True
        assert Image.query.filter_by(source_type="dataset").count() == 0
