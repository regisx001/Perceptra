import os
import subprocess
import sys
import time
from pathlib import Path
import click
from flask.cli import FlaskGroup, with_appcontext

from src.app import create_app


def create_cli_app():
    return create_app()


@click.group(cls=FlaskGroup, create_app=create_cli_app)
def cli():
    """Perceptra management CLI."""
    pass


@cli.command("serve")
@click.option("--bind", "-b", default=None, help="Server socket bind address (default from gunicorn.conf.py).")
@click.option("--workers", "-w", default=None, type=int, help="Number of worker processes.")
@click.option("--threads", "-t", default=None, type=int, help="Number of threads per worker.")
def serve(bind=None, workers=None, threads=None):
    """Run production Gunicorn server."""
    cmd = ["gunicorn", "--config", "gunicorn.conf.py"]
    if bind:
        cmd.extend(["--bind", bind])
    if workers:
        cmd.extend(["--workers", str(workers)])
    if threads:
        cmd.extend(["--threads", str(threads)])
    cmd.append("src.app:create_app()")
    sys.exit(subprocess.call(cmd))


@cli.command("dev")
@click.option("--port", "-p", default=7000, help="Port to run the dev server on (default 7000).")
@click.option("--host", "-h", default="127.0.0.1", help="Host to bind to.")
def dev_cmd(port=7000, host="127.0.0.1"):
    """Run Flask development server."""
    _run_dev(port=port, host=host)


def _run_dev(port=None, host="127.0.0.1"):
    if port is None:
        port = int(os.getenv("DEV_PORT", os.getenv("PORT", 7000)))
    os.environ.setdefault("FLASK_APP", "src.app:create_app")
    cmd = ["flask", "--app", "src.app:create_app", "run", "--port", str(port), "--host", host, "--debug"] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))


def dev():
    """Standalone entry point for uv run dev."""
    _run_dev()


def db_upgrade():
    """Shortcut command to run database upgrade."""
    cmd = ["flask", "--app", "src.app:create_app", "db", "upgrade"] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))


def db_migrate():
    """Shortcut command to generate a new migration."""
    cmd = ["flask", "--app", "src.app:create_app", "db", "migrate"] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))


# ============================================================================
# Dataset Ingestion Commands
# ============================================================================

@cli.group("dataset")
def dataset_group():
    """Manage and ingest image datasets into Perceptra."""
    pass


def _execute_ingest(
    folder: str,
    name: str | None,
    user: str | None,
    batch_size: int,
    limit: int | None,
    compute_features: bool,
    skip_existing: bool,
    workers: int,
    parent_category: bool,
):
    from flask import current_app
    from src.services.dataset_service import DatasetIngestionService

    folder_path = Path(folder).resolve()
    if not folder_path.exists():
        click.secho(f"Error: Folder '{folder_path}' does not exist.", fg="red", err=True)
        sys.exit(1)

    ds_name = name or folder_path.name
    storage_root = current_app.config.get("STORAGE_BASE_PATH", "storage")
    service = DatasetIngestionService(storage_root=storage_root)

    click.echo()
    click.secho("╔══════════════════════════════════════════════════════════════════╗", fg="cyan")
    click.secho(f"║ PERCEPTRA DATASET INGESTION: {ds_name[:34]:<34} ║", fg="cyan", bold=True)
    click.secho("╚══════════════════════════════════════════════════════════════════╝", fg="cyan")
    click.echo(f"  • Source Folder      : {click.style(str(folder_path), fg='bright_blue')}")
    click.echo(f"  • Target Storage     : {click.style(str(Path(storage_root).resolve()), fg='bright_blue')}")
    click.echo(f"  • Compute Features   : {click.style('Yes (5 CBIR Descriptors)' if compute_features else 'No', fg='green' if compute_features else 'yellow')}")
    click.echo(f"  • Skip Existing      : {click.style(str(skip_existing), fg='white')}")
    click.echo(f"  • Batch Commit Size  : {click.style(str(batch_size), fg='white')}")
    click.echo(f"  • Worker Threads     : {click.style(str(workers), fg='white')}")
    if limit:
        click.echo(f"  • Max Images (Limit) : {click.style(str(limit), fg='yellow')}")
    click.echo()

    # Pre-scan inspection
    scanned = service.scan_folder(folder_path)
    total_files = sum(len(files) for files in scanned.values())
    if not total_files:
        click.secho(f"No supported image files (.jpg, .jpeg, .png, .webp, .bmp) found in '{folder_path}'.", fg="yellow")
        return

    click.secho(f"Discovered {total_files:,} images across {len(scanned)} categories:", fg="bright_white", bold=True)
    for cat_name, file_list in scanned.items():
        click.echo(f"  - {click.style(cat_name, fg='yellow')}: {len(file_list):,} images")
    click.echo()

    target_total = min(total_files, limit) if limit else total_files

    with click.progressbar(
        length=target_total,
        label=click.style("Ingesting & Extracting Descriptors", fg="green"),
        show_eta=True,
        show_percent=True,
        item_show_func=lambda item: f"[{item}]" if item else "",
    ) as bar:
        def on_progress(current, total, filename, cat_name):
            bar.update(1, current_item=f"{cat_name}/{filename[:20]}")

        stats = service.ingest_dataset(
            folder_path=folder_path,
            dataset_name=ds_name,
            user_email=user,
            batch_size=batch_size,
            limit=limit,
            compute_features=compute_features,
            skip_existing=skip_existing,
            create_parent_category=parent_category,
            max_workers=workers,
            progress_callback=on_progress,
        )

    click.echo()
    click.secho("✓ Ingestion Completed Successfully!", fg="green", bold=True)
    click.echo(f"  • Duration            : {stats.duration_seconds:.2f} seconds")
    if stats.ingested > 0 and stats.duration_seconds > 0:
        click.echo(f"  • Throughput          : {stats.ingested / stats.duration_seconds:.1f} images/sec")
    click.echo(f"  • Images Ingested     : {click.style(f'{stats.ingested:,}', fg='green', bold=True)}")
    click.echo(f"  • Images Skipped      : {click.style(f'{stats.skipped:,}', fg='white')}")
    click.echo(f"  • Images Failed       : {click.style(f'{stats.failed:,}', fg='red' if stats.failed > 0 else 'white')}")
    click.echo(f"  • Descriptors Indexed : {click.style(f'{stats.features_computed:,}', fg='cyan', bold=True)}")
    click.echo()

    if stats.errors:
        click.secho(f"Errors encountered ({len(stats.errors)}):", fg="red", bold=True)
        for err in stats.errors[:10]:
            click.secho(f"  • {err}", fg="red")
        if len(stats.errors) > 10:
            click.echo(f"  ... and {len(stats.errors) - 10} more errors.")
        click.echo()


@dataset_group.command("ingest")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--name", "-n", default=None, help="Dataset name (defaults to folder directory name).")
@click.option("--user", "-u", default=None, help="Optional user email if importing into a specific user's personal library instead of global dataset (defaults to None for isolated dataset).")
@click.option("--batch-size", "-b", default=50, show_default=True, type=int, help="Database commit batch size.")
@click.option("--limit", "-l", default=None, type=int, help="Maximum number of images to ingest (for testing).")
@click.option("--compute-features/--no-compute-features", default=True, show_default=True, help="Compute all 5 CBIR descriptors.")
@click.option("--skip-existing/--force", default=True, show_default=True, help="Skip images that already exist in database.")
@click.option("--workers", "-w", default=4, show_default=True, type=int, help="Number of worker threads for parallel extraction.")
@click.option("--parent/--no-parent", "parent_category", default=True, show_default=True, help="Create a parent category for the dataset.")
@with_appcontext
def dataset_ingest(folder, name, user, batch_size, limit, compute_features, skip_existing, workers, parent_category):
    """
    Ingest images from a folder into Perceptra, organize categories, and compute visual descriptors.
    """
    _execute_ingest(folder, name, user, batch_size, limit, compute_features, skip_existing, workers, parent_category)


# Top-level shortcut alias: perceptra ingest-dataset <folder>
@cli.command("ingest-dataset")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--name", "-n", default=None, help="Dataset name (defaults to folder directory name).")
@click.option("--user", "-u", default=None, help="User email to associate categories with.")
@click.option("--batch-size", "-b", default=50, show_default=True, type=int, help="Database commit batch size.")
@click.option("--limit", "-l", default=None, type=int, help="Maximum number of images to ingest.")
@click.option("--compute-features/--no-compute-features", default=True, show_default=True, help="Compute all 5 CBIR descriptors.")
@click.option("--skip-existing/--force", default=True, show_default=True, help="Skip images that already exist in database.")
@click.option("--workers", "-w", default=4, show_default=True, type=int, help="Number of worker threads for parallel extraction.")
@click.option("--parent/--no-parent", "parent_category", default=True, show_default=True, help="Create a parent category for the dataset.")
@with_appcontext
def ingest_dataset_alias(folder, name, user, batch_size, limit, compute_features, skip_existing, workers, parent_category):
    """
    Shortcut for 'perceptra dataset ingest <folder>'.
    """
    _execute_ingest(folder, name, user, batch_size, limit, compute_features, skip_existing, workers, parent_category)


@dataset_group.command("status")
@click.option("--dataset", "-d", default=None, help="Filter status by dataset name.")
@with_appcontext
def dataset_status(dataset=None):
    """
    Display current dataset counts, categories, and feature extraction statistics.
    """
    from sqlalchemy import func
    from src.models.category import Category
    from src.models.image import Image
    from src.models.image_feature import ImageFeature

    click.echo()
    click.secho("╔══════════════════════════════════════════════════════════════════╗", fg="cyan")
    click.secho("║ PERCEPTRA DATASET & FEATURE STATUS                               ║", fg="cyan", bold=True)
    click.secho("╚══════════════════════════════════════════════════════════════════╝", fg="cyan")

    total_images = Image.query.count()
    dataset_images = Image.query.filter_by(source_type="dataset").count()
    uploaded_images = Image.query.filter(Image.source_type.in_(["upload", "derived"])).count()
    indexed_images = Image.query.filter_by(processing_status="indexed").count()
    pending_images = Image.query.filter_by(processing_status="pending").count()
    failed_images = Image.query.filter_by(processing_status="failed").count()

    click.echo(f"  • Total Images in DB  : {click.style(f'{total_images:,}', fg='bright_white', bold=True)}")
    click.echo(f"    - Dataset Images    : {click.style(f'{dataset_images:,}', fg='green')}")
    click.echo(f"    - User Uploads      : {click.style(f'{uploaded_images:,}', fg='blue')}")
    click.echo(f"  • Processing Status   :")
    click.echo(f"    - Indexed           : {click.style(f'{indexed_images:,}', fg='green')}")
    click.echo(f"    - Pending           : {click.style(f'{pending_images:,}', fg='yellow')}")
    click.echo(f"    - Failed            : {click.style(f'{failed_images:,}', fg='red' if failed_images > 0 else 'white')}")
    click.echo()

    # Features Breakdown
    feature_counts = (
        ImageFeature.query.with_entities(ImageFeature.feature_type, func.count(ImageFeature.id))
        .group_by(ImageFeature.feature_type)
        .all()
    )
    click.secho("Feature Descriptors Indexed:", fg="cyan", bold=True)
    if feature_counts:
        for ftype, cnt in sorted(feature_counts, key=lambda x: x[0]):
            styled_name = click.style(f"{ftype:<20}", fg="bright_cyan")
            click.echo(f"  • {styled_name} : {cnt:,} vectors")
    else:
        click.echo("  No features indexed yet.")
    click.echo()

    # Categories Breakdown
    categories = Category.query.all()
    click.secho(f"Categories ({len(categories):,} total):", fg="cyan", bold=True)
    for cat in categories[:25]:
        cat_count = Image.query.filter_by(category_id=cat.id).count()
        parent_info = f" (parent: {cat.parent.name})" if cat.parent else " [root]"
        click.echo(f"  • {click.style(cat.name, fg='yellow')}{parent_info}: {cat_count:,} images")
    if len(categories) > 25:
        click.echo(f"  ... and {len(categories) - 25} more categories.")
    click.echo()
