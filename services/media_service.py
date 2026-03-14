"""Helpers for working with Anki collection.media files."""

import logging
import sys
from pathlib import Path

from aqt import mw

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def get_media_folder_path():
    """Return path to current collection media directory."""
    media_dir = mw.col.media.dir()
    return Path(media_dir)


def build_media_file_path(filename):
    """Build absolute media path for a filename."""
    media_folder = get_media_folder_path()
    return media_folder / filename


def media_file_exists(filename):
    """Check if a media file already exists in collection media folder."""
    file_path = build_media_file_path(filename)
    logger.info(f"Media file path: {file_path}")
    return file_path.exists()


def write_media_file(filename, data):
    """Write binary content to collection media and return resulting path."""
    file_path = build_media_file_path(filename)
    file_path.write_bytes(data)
    return file_path
