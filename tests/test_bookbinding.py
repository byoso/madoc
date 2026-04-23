import os
import sys
from pathlib import Path

import pytest

from madoc.bookbinding.entrypoint import cmd as bookbinding_cmd
from madoc.bookbinding.entrypoint import _build_icon_url
from madoc.bookbinding.entrypoint import _build_page_url
from madoc.bookbinding.entrypoint import _prepare_ordered_entries
from madoc.bookbinding.entrypoint import _resolve_page_label


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


def test_resolve_page_label_strips_html_suffix_when_title_missing(tmp_path: Path) -> None:
    page = tmp_path / "sample.html"
    page.write_text("<html><body>No title</body></html>", encoding="utf-8")

    label = _resolve_page_label(str(page))

    assert label == "sample"


def test_bookbinding_cmd_get_css_copies_default_css(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["madoc-bb", "--get-css"])

    bookbinding_cmd()

    copied_css = tmp_path / "madoc_style.css"
    assert copied_css.is_file()
    assert copied_css.read_text(encoding="utf-8")


def test_bookbinding_cmd_uses_custom_css(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    page = tmp_path / "doc.html"
    page.write_text("<html><head><title>Doc</title></head><body>Hello</body></html>", encoding="utf-8")

    custom_css = tmp_path / "custom.css"
    custom_css.write_text("/* bb-custom-css-marker */\nbody { border: 0; }", encoding="utf-8")

    output_dir = tmp_path / "out"
    output_dir.mkdir()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "madoc-bb",
            "-p",
            str(page),
            "--css",
            str(custom_css),
            "-o",
            str(output_dir),
        ],
    )

    bookbinding_cmd()

    output_html = output_dir / "madoc-bookbinding.html"
    assert output_html.is_file()
    html = output_html.read_text(encoding="utf-8")
    assert "bb-custom-css-marker" in html
