import os
from pathlib import Path

import pytest

from madoc.bookbinding.entrypoint import _build_icon_url
from madoc.bookbinding.entrypoint import _build_page_url
from madoc.bookbinding.entrypoint import _prepare_ordered_entries


def test_prepare_ordered_entries_keeps_page_icon_pairing(tmp_path: Path) -> None:
    page1 = tmp_path / "a.html"
    page2 = tmp_path / "b.html"
    icon = tmp_path / "icon.png"
    page1.write_text("<title>A</title>", encoding="utf-8")
    page2.write_text("<title>B</title>", encoding="utf-8")
    icon.write_bytes(b"png")

    chain = [
        ("page", str(page1)),
        ("icon", str(icon)),
        ("page", str(page2)),
    ]

    entries = _prepare_ordered_entries(chain, launch_dir=str(tmp_path))

    assert len(entries) == 2
    assert entries[0]["page"] == str(page1)
    assert entries[0]["icon"] == str(icon)
    assert entries[1]["page"] == str(page2)
    assert entries[1]["icon"] is None


def test_prepare_ordered_entries_rejects_icon_before_page(tmp_path: Path) -> None:
    icon = tmp_path / "icon.png"
    icon.write_bytes(b"png")

    with pytest.raises(ValueError):
        _prepare_ordered_entries([("icon", str(icon))], launch_dir=str(tmp_path))


def test_build_page_and_icon_urls_no_b64_are_relative(tmp_path: Path) -> None:
    output_dir = tmp_path / "dist"
    pages_dir = tmp_path / "pages"
    output_dir.mkdir()
    pages_dir.mkdir()

    page = pages_dir / "doc.html"
    icon = pages_dir / "icon.png"
    page.write_text("<html><head><title>Doc</title></head><body>x</body></html>", encoding="utf-8")
    icon.write_bytes(b"png")

    page_url = _build_page_url(str(page), output_dir=str(output_dir), no_b64=True)
    icon_url = _build_icon_url(str(icon), output_dir=str(output_dir), no_b64=True)

    expected_page = os.path.relpath(page, start=output_dir).replace(os.sep, "/")
    expected_icon = os.path.relpath(icon, start=output_dir).replace(os.sep, "/")

    assert page_url == expected_page
    assert icon_url == expected_icon


def test_build_page_url_b64_embeds_html(tmp_path: Path) -> None:
    output_dir = tmp_path / "dist"
    output_dir.mkdir()

    page = tmp_path / "doc.html"
    page.write_text("<html><body>Hello</body></html>", encoding="utf-8")

    page_url = _build_page_url(str(page), output_dir=str(output_dir), no_b64=False)
    assert page_url.startswith("data:text/html;base64,")
