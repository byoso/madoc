import base64
import os
import re
import zipfile


def _is_local_resource(path: str) -> bool:
    if not path:
        return False
    normalized = path.strip().lower()
    return not (normalized.startswith("http://") or normalized.startswith("https://") or normalized.startswith("data:"))


def extract_local_resource_paths(text: str, base_dir: str | None = None) -> set[str]:
    """Detect local referenced files from markdown and HTML link/img patterns."""
    paths = set()
    root_dir = os.path.abspath(base_dir or os.getcwd())

    # Markdown image and link patterns
    md_pattern = re.compile(r"!\[.*?\]\(([^)]+)\)|\[[^\]]*\]\(([^)]+)\)")
    for match in md_pattern.finditer(text):
        resource = match.group(1) or match.group(2)
        if not resource:
            continue
        resource = resource.split("#")[0].split("?")[0].strip()
        candidate = resource if os.path.isabs(resource) else os.path.join(root_dir, resource)
        if _is_local_resource(resource) and os.path.isfile(candidate):
            paths.add(os.path.abspath(candidate))

    # HTML img src and a href
    html_pattern = re.compile(r"<(?:img|a)[^>]+?(?:src|href)=[\'\"](.*?)[\'\"][^>]*>", re.IGNORECASE)
    for match in html_pattern.finditer(text):
        resource = match.group(1)
        if not resource:
            continue
        resource = resource.split("#")[0].split("?")[0].strip()
        candidate = resource if os.path.isabs(resource) else os.path.join(root_dir, resource)
        if _is_local_resource(resource) and os.path.isfile(candidate):
            paths.add(os.path.abspath(candidate))

    return paths


def create_zip_from_files(
    files: list[str],
    extra_files: list[str] | None = None,
    output_dir: str | None = None,
    base_dir: str | None = None,
) -> str:
    """Create a zip archive with the provided files and optional extra files.

    - `files`: source markdown files (raw content)
    - `extra_files`: related local resources (raw content)

    Returns archive file name (basename).
    """
    all_files = list(files or [])
    if extra_files:
        for f in extra_files:
            if f and f not in all_files:
                all_files.append(f)

    if not all_files:
        return ""

    archive_name = "madoc_sources.zip"
    output_root = os.path.abspath(output_dir or os.getcwd())
    archive_path = os.path.join(output_root, archive_name)
    archive_base_dir = os.path.abspath(base_dir or output_root)

    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filepath in all_files:
            if not filepath:
                continue

            abs_path = os.path.abspath(filepath)
            if not os.path.isfile(abs_path):
                continue

            if abs_path == archive_path:
                continue

            if os.path.commonpath([abs_path, archive_base_dir]) == archive_base_dir:
                arcname = os.path.relpath(abs_path, start=archive_base_dir)
            else:
                arcname = os.path.basename(abs_path)
            archive.write(abs_path, arcname=arcname)

    return archive_path
