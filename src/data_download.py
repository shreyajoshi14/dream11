"""Download + unzip Cricsheet ball-by-ball JSON (programmatic, as required)."""
import io, zipfile, requests
from .config import RAW_DIR, CRICSHEET_URL


def download(force=False):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if any(RAW_DIR.glob("*.json")) and not force:
        print("raw data already present:", len(list(RAW_DIR.glob('*.json'))), "files")
        return
    print("downloading", CRICSHEET_URL)
    r = requests.get(CRICSHEET_URL, timeout=600)
    r.raise_for_status()
    zipfile.ZipFile(io.BytesIO(r.content)).extractall(RAW_DIR)
    print("done:", len(list(RAW_DIR.glob('*.json'))), "files")


if __name__ == "__main__":
    download()
