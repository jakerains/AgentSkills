#!/usr/bin/env python3
"""
Upload a knowledge base folder structure to ElevenLabs.

Discovers subdirectories and supported files, creates matching folders in
ElevenLabs, uploads each file into its folder, optionally triggers RAG
indexing, and writes a manifest JSON for use with deploy_with_tools.py.

Usage:
    python deploy_kb.py <kb_dir> [options]

Arguments:
    kb_dir              Local directory containing KB content. Each subdirectory
                        becomes a folder in ElevenLabs; files inside are uploaded.
                        Files at the root of kb_dir are uploaded without a folder.

Options:
    --root-name NAME    Name for the ElevenLabs root folder (default: directory name)
    --manifest PATH     Where to write the manifest JSON (default: <kb_dir>/kb_manifest.json)
    --skip-rag          Skip RAG index triggering (faster, but docs won't be
                        searchable until indexed by ElevenLabs automatically)
    --embedding-model   Embedding model for RAG indexing (default: e5_mistral_7b_instruct)
    --dry-run           Show what would be uploaded without making API calls

Requires:
    ELEVENLABS_API_KEY environment variable
    pip install requests
"""
import argparse
import json
from dotenv import load_dotenv

load_dotenv()
import os
import sys
import time
import requests
from pathlib import Path

BASE_URL = "https://api.elevenlabs.io/v1"

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".html", ".htm", ".epub", ".docx"}

CONTENT_TYPE_MAP = {
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".pdf": "application/pdf",
    ".html": "text/html",
    ".htm": "text/html",
    ".epub": "application/epub+zip",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def get_headers(api_key: str) -> dict:
    return {"xi-api-key": api_key}


def validate_key(api_key: str) -> bool:
    try:
        r = requests.get(f"{BASE_URL}/voices", headers=get_headers(api_key), timeout=15)
        return r.ok
    except Exception:
        return False


def create_folder(api_key: str, name: str, parent_folder_id: str = None) -> dict:
    payload = {"name": name}
    if parent_folder_id:
        payload["parent_folder_id"] = parent_folder_id

    r = requests.post(
        f"{BASE_URL}/convai/knowledge-base/folder",
        headers={**get_headers(api_key), "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if not r.ok:
        raise Exception(f"Failed to create folder '{name}': {r.status_code} {r.text[:300]}")
    return r.json()


def upload_file(api_key: str, file_path: Path, parent_folder_id: str = None) -> dict:
    data = {}
    if parent_folder_id:
        data["parent_folder_id"] = parent_folder_id

    content_type = CONTENT_TYPE_MAP.get(file_path.suffix.lower(), "application/octet-stream")

    with open(file_path, "rb") as f:
        r = requests.post(
            f"{BASE_URL}/convai/knowledge-base/file",
            headers=get_headers(api_key),
            data=data,
            files={"file": (file_path.name, f, content_type)},
            timeout=120,
        )
    if not r.ok:
        raise Exception(f"Failed to upload '{file_path.name}': {r.status_code} {r.text[:300]}")
    return r.json()


def wait_for_rag_index(
    api_key: str, doc_id: str, embedding_model: str = "e5_mistral_7b_instruct", max_wait: int = 120
) -> bool:
    r = requests.post(
        f"{BASE_URL}/convai/knowledge-base/{doc_id}/rag-index",
        headers={**get_headers(api_key), "Content-Type": "application/json"},
        json={"model": embedding_model},
        timeout=30,
    )
    if not r.ok:
        print(f"    Warning: RAG index trigger failed for {doc_id}: {r.status_code}")
        return False

    elapsed = 0
    interval = 3
    while elapsed < max_wait:
        time.sleep(interval)
        elapsed += interval
        r = requests.post(
            f"{BASE_URL}/convai/knowledge-base/{doc_id}/rag-index",
            headers={**get_headers(api_key), "Content-Type": "application/json"},
            json={"model": embedding_model},
            timeout=30,
        )
        if r.ok:
            status = r.json().get("status", "")
            if status == "SUCCEEDED":
                return True
            if status == "FAILED":
                print(f"    Warning: RAG indexing failed for {doc_id}")
                return False
        interval = min(interval * 2, 15)

    print(f"    Warning: RAG indexing timed out for {doc_id}")
    return False


def collect_files(kb_dir: Path) -> tuple[list[tuple[str | None, Path]], list[str]]:
    """Discover subdirectories and supported files.

    Returns (files, folder_names) where files is a list of
    (folder_name_or_None, file_path) tuples.
    """
    files = []
    folder_names = []

    for item in sorted(kb_dir.iterdir()):
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append((None, item))

    for item in sorted(kb_dir.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            folder_names.append(item.name)
            for f in sorted(item.iterdir()):
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                    files.append((item.name, f))

    return files, folder_names


def main():
    parser = argparse.ArgumentParser(
        description="Upload a knowledge base folder to ElevenLabs"
    )
    parser.add_argument("kb_dir", type=Path, help="Directory containing KB content")
    parser.add_argument("--root-name", type=str, help="ElevenLabs root folder name (default: directory name)")
    parser.add_argument("--manifest", type=Path, help="Manifest output path (default: <kb_dir>/kb_manifest.json)")
    parser.add_argument("--skip-rag", action="store_true", help="Skip RAG index triggering")
    parser.add_argument("--embedding-model", type=str, default="e5_mistral_7b_instruct",
                        help="Embedding model for RAG indexing")
    parser.add_argument("--dry-run", action="store_true", help="Preview without API calls")
    args = parser.parse_args()

    if not args.kb_dir.is_dir():
        print(f"Error: Not a directory: {args.kb_dir}")
        sys.exit(1)

    root_name = args.root_name or args.kb_dir.name
    manifest_path = args.manifest or (args.kb_dir / "kb_manifest.json")

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set")
        print("  export ELEVENLABS_API_KEY='your-api-key-here'")
        sys.exit(1)

    if not args.dry_run:
        print("Validating API key...")
        if not validate_key(api_key):
            print("Error: Invalid API key")
            sys.exit(1)
        print("API key valid!\n")

    files, folder_names = collect_files(args.kb_dir)
    if not files:
        print(f"No supported files found in {args.kb_dir}")
        print(f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
        sys.exit(1)

    print(f"Knowledge base: {len(files)} files across {len(folder_names)} folders")
    print(f"Root folder name: {root_name}\n")

    total_size = 0
    for folder_name, file_path in files:
        size = file_path.stat().st_size
        total_size += size
        prefix = f"{folder_name}/" if folder_name else ""
        print(f"  {prefix}{file_path.name} ({size:,} bytes)")
    print(f"\n  Total: {total_size:,} bytes ({total_size / 1024:.1f} KB)")

    if args.dry_run:
        print("\n[DRY RUN] Would create folders and upload files.")
        sys.exit(0)

    confirm = input("\nUpload all files? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(0)

    # Create root folder
    print(f"\nCreating root folder: {root_name}")
    root = create_folder(api_key, root_name)
    root_folder_id = root["id"]
    print(f"  Root folder ID: {root_folder_id}")

    # Create subfolders
    folder_id_map = {}
    for fname in folder_names:
        print(f"  Creating subfolder: {fname}")
        folder = create_folder(api_key, fname, parent_folder_id=root_folder_id)
        folder_id_map[fname] = folder["id"]
        print(f"    Folder ID: {folder['id']}")

    # Upload files
    print("\n" + "-" * 50)
    print("Uploading files...")
    print("-" * 50)

    uploaded_docs = []
    for i, (folder_name, file_path) in enumerate(files, 1):
        parent_id = folder_id_map.get(folder_name) if folder_name else root_folder_id
        prefix = f"{folder_name}/" if folder_name else ""
        print(f"\n  [{i}/{len(files)}] {prefix}{file_path.name}")

        result = upload_file(api_key, file_path, parent_folder_id=parent_id)
        doc_id = result.get("id")
        doc_name = result.get("name", file_path.stem)
        print(f"    Document ID: {doc_id}")

        if doc_id:
            doc_entry = {
                "id": doc_id,
                "name": doc_name,
                "usage_mode": "auto",
            }
            if folder_name:
                doc_entry["folder"] = folder_name
            uploaded_docs.append(doc_entry)

    print(f"\n  Uploaded {len(uploaded_docs)}/{len(files)} documents.")

    # RAG indexing
    if not args.skip_rag and uploaded_docs:
        print("\n" + "-" * 50)
        print("Triggering RAG indexing...")
        print("-" * 50)
        indexed = 0
        for i, doc in enumerate(uploaded_docs, 1):
            print(f"  [{i}/{len(uploaded_docs)}] {doc['name']}...", end=" ", flush=True)
            if wait_for_rag_index(api_key, doc["id"], args.embedding_model):
                print("OK")
                indexed += 1
            else:
                print("FAILED")
        print(f"\n  Indexed {indexed}/{len(uploaded_docs)} documents.")

    # Write manifest
    manifest = {
        "root_folder_id": root_folder_id,
        "root_folder_name": root_name,
        "embedding_model": args.embedding_model,
        "folders": folder_id_map,
        "documents": uploaded_docs,
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved: {manifest_path}")

    print("\n" + "=" * 50)
    print("SUCCESS!")
    print("=" * 50)
    print(f"  Root folder: {root_folder_id}")
    print(f"  Folders: {len(folder_id_map)}")
    print(f"  Documents: {len(uploaded_docs)}")
    print(f"\nUse with deploy_with_tools.py:")
    print(f"  python deploy_with_tools.py agent.json --kb-manifest {manifest_path}")


if __name__ == "__main__":
    main()
