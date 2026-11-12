import os
import subprocess
import sys
import click
from flask.cli import FlaskGroup
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


def _run_dev(port=7000, host="127.0.0.1"):
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
