"""Download the WHO mhGAP starter guideline from the official WHO repository."""
from pathlib import Path
import json
import sys
import requests

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
DOC = MANIFEST["documents"][0]
TARGET_DIR = ROOT / "pdfs"
TARGET = TARGET_DIR / DOC["filename"]


def main() -> int:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    if TARGET.exists() and TARGET.stat().st_size > 100_000:
        print(f"Dataset already exists: {TARGET}")
        print("Delete the file and rerun this script to download it again.")
        return 0

    print(f"Downloading: {DOC['title']}")
    print(f"Source: {DOC['download_url']}")
    try:
        response = requests.get(
            DOC["download_url"],
            headers={"User-Agent": "ClinicalProtocolRAG/1.0 (research prototype)"},
            timeout=(20, 180),
            stream=True,
        )
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()
        first = next(response.iter_content(chunk_size=8192), b"")
        if not first.startswith(b"%PDF") and "pdf" not in content_type:
            raise RuntimeError(
                "The WHO endpoint did not return a PDF. Open the official source page "
                "and download the PDF manually into dataset/pdfs/."
            )
        with TARGET.open("wb") as output:
            output.write(first)
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output.write(chunk)
        if TARGET.stat().st_size < 100_000:
            TARGET.unlink(missing_ok=True)
            raise RuntimeError("Downloaded file is unexpectedly small; download rejected.")
        print(f"Saved {TARGET} ({TARGET.stat().st_size:,} bytes)")
        print("Please review the publication licence before reuse or redistribution.")
        return 0
    except Exception as exc:
        TARGET.unlink(missing_ok=True)
        print(f"Download failed: {exc}", file=sys.stderr)
        print(f"Manual source: {DOC['source_page']}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
