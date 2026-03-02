"""Simple utility script to package ChatGlyo Python files for distribution."""

from pathlib import Path
import zipfile

FILES = ["chatglyo_gui.py", "chatglyo_browser.py", "chatglyo_download_hub.py", "README.md"]
OUT = "chatglyo_bundle.zip"


def create_bundle():
    base = Path(__file__).resolve().parent
    out_path = base / OUT
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_name in FILES:
            path = base / file_name
            if path.exists():
                zf.write(path, arcname=file_name)
                print(f"Added: {file_name}")
            else:
                print(f"Skipped (missing): {file_name}")
    print(f"Bundle created: {out_path}")


if __name__ == "__main__":
    create_bundle()
