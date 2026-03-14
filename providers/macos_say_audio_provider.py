import shutil
import subprocess
import tempfile
from pathlib import Path


def normalize_text(text):
    return text.strip()


def generate_audio_data_with_say(text):
    normalized_text = normalize_text(text)

    if not normalized_text:
        return None

    if shutil.which("say") is None:
        return None

    temp_file = tempfile.NamedTemporaryFile(suffix=".aiff", delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()

    try:
        command = [
            "say",
            "-o",
            str(temp_path),
            normalized_text,
        ]

        completed_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if completed_process.returncode != 0:
            return None

        if not temp_path.exists():
            return None

        return temp_path.read_bytes()
    finally:
        if temp_path.exists():
            temp_path.unlink()
