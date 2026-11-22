"""
Pack and fetch the corpus data that is deliberately kept out of git.

data/ (21 source PDFs, ~30 MB, and chunks.json with stored embeddings,
~90 MB) is versioned as a GitHub Release asset instead of in git history:
binary blobs never diff, and every version committed stays in every clone
forever.

    python scripts/data_bundle.py pack
        -> dist/ip-sakti-data-<date>.tar.gz + .sha256, and prints the
           `gh release create` command to publish it (not run for you)

    python scripts/data_bundle.py fetch [--tag data-2026-11-22] [--url URL]
        -> downloads the bundle (gh CLI by default, or any URL), checks the
           SHA-256, extracts into data/, and verifies every file against the
           bundle's manifest

After fetching, load the stored vectors into Qdrant without re-embedding:

    python scripts/sync_qdrant.py --apply

Rebuilding from the PDFs alone instead (re-chunks and re-embeds everything):

    PYTHONPATH=src python src/ingest.py && python scripts/sync_qdrant.py --apply --prune
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
MANIFEST_NAME = "data/BUNDLE_MANIFEST.json"

# What the app and the ingest scripts need; app.db (per-user audit/consent
# rows) and backups are never bundled.
INCLUDE = [
    "data/raw/*.pdf",
    "data/processed/chunks.json",
    "data/processed/chunks_web.json",
    "data/processed/web_sources_manifest.json",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def pack(_args) -> None:
    files = sorted({p for pattern in INCLUDE for p in ROOT.glob(pattern) if p.is_file()})
    if not files:
        sys.exit("nothing to pack: data/ is empty")

    entries: dict[str, dict] = {
        str(p.relative_to(ROOT)): {"bytes": p.stat().st_size, "sha256": _sha256(p)} for p in files
    }
    manifest = {"created": date.today().isoformat(), "files": entries}
    DIST.mkdir(exist_ok=True)
    name = f"ip-sakti-data-{manifest['created']}"
    bundle = DIST / f"{name}.tar.gz"

    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = Path(tmp) / "BUNDLE_MANIFEST.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        with tarfile.open(bundle, "w:gz") as tar:
            for p in files:
                tar.add(p, arcname=str(p.relative_to(ROOT)))
            tar.add(manifest_path, arcname=MANIFEST_NAME)

    checksum = DIST / f"{name}.tar.gz.sha256"
    checksum.write_text(f"{_sha256(bundle)}  {bundle.name}\n")

    total = sum(f["bytes"] for f in entries.values())
    print(f"packed {len(files)} files ({total / 1e6:.1f} MB) -> {bundle.relative_to(ROOT)}")
    print("\npublish it with:\n")
    print(f"  gh release create data-{manifest['created']} {bundle.relative_to(ROOT)} {checksum.relative_to(ROOT)} \\")
    print(f"    --title 'Corpus data {manifest['created']}' --notes 'scripts/data_bundle.py fetch --tag data-{manifest['created']}'")


def _download(args, dest: Path) -> tuple[Path, Path | None]:
    if args.url:
        bundle = dest / Path(args.url).name
        urllib.request.urlretrieve(args.url, bundle)  # noqa: S310 - operator-supplied URL
        return bundle, None

    if not shutil.which("gh"):
        sys.exit("gh CLI not found: install it, or pass --url to the .tar.gz asset")
    cmd = ["gh", "release", "download", "--dir", str(dest), "--pattern", "ip-sakti-data-*"]
    if args.tag:
        cmd.insert(3, args.tag)
    subprocess.run(cmd, check=True, cwd=ROOT)
    bundle = next(dest.glob("*.tar.gz"))
    checksum = next(dest.glob("*.sha256"), None)
    return bundle, checksum


def _safe_members(tar: tarfile.TarFile):
    for member in tar.getmembers():
        path = Path(member.name)
        if path.is_absolute() or ".." in path.parts or path.parts[0] != "data" or not member.isfile():
            sys.exit(f"refusing unsafe archive member: {member.name}")
        yield member


def fetch(args) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bundle, checksum = _download(args, Path(tmp))

        if checksum is not None:
            expected = checksum.read_text().split()[0]
            if _sha256(bundle) != expected:
                sys.exit(f"checksum mismatch for {bundle.name}: download is corrupt or tampered with")
            print(f"checksum ok: {bundle.name}")

        with tarfile.open(bundle, "r:gz") as tar:
            tar.extractall(ROOT, members=list(_safe_members(tar)))  # noqa: S202 - members validated above

    manifest = json.loads((ROOT / MANIFEST_NAME).read_text())
    bad = [rel for rel, meta in manifest["files"].items() if _sha256(ROOT / rel) != meta["sha256"]]
    if bad:
        sys.exit(f"{len(bad)} files failed verification: {bad[:5]}")
    print(f"extracted and verified {len(manifest['files'])} files into data/ (bundle of {manifest['created']})")
    print("next: python scripts/sync_qdrant.py --apply")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("pack", help="bundle data/ into dist/").set_defaults(func=pack)
    fetch_parser = sub.add_parser("fetch", help="download and extract a bundle into data/")
    fetch_parser.add_argument("--tag", help="release tag (default: latest release)")
    fetch_parser.add_argument("--url", help="direct URL to a .tar.gz bundle instead of gh")
    fetch_parser.set_defaults(func=fetch)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
