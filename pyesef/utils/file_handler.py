"""File handlers."""

import shutil
import zipfile


def unzip_file(zip_file: str, extract_to: str) -> None:
    """Unzip a ZIP file to the specified directory."""
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def delete_folder(folder_path: str) -> None:
    """Delete the specified folder and its contents."""
    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass
