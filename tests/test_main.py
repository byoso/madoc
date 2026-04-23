import sys
import zipfile
from pathlib import Path

import pytest

from madoc.main import cmd as madoc_cmd
from madoc.main import main as generate_main
from madoc.main import rewrite_internal_md_links


def test_rewrite_internal_md_links_rewrites_known_md_targets() -> None:
    html = '<p><a href="(02)page_beta.md">Beta</a> <a href="https://example.com">ext</a></p>'
    mapping = {"(02)page_beta.md": 2}

    updated = rewrite_internal_md_links(html, mapping)

    assert 'onclick="display(2)"' in updated
    assert 'href="javascript:void(0)"' in updated
    assert 'href="https://example.com"' in updated


def test_main_generates_html_and_relative_sources_zip(tmp_path: Path) -> None:
    source_dir = tmp_path / "src"
    output_dir = tmp_path / "out"
    source_dir.mkdir()
    output_dir.mkdir()

    (source_dir / "(01)alpha.md").write_text("# Alpha", encoding="utf-8")
    (source_dir / "(02)beta.md").write_text("[Go Alpha]((01)alpha.md)", encoding="utf-8")

    generate_main(
        source_dir=str(source_dir),
        output_dir=str(output_dir),
        title="Test",
        add_src=True,
        no_b64=True,
    )

    output_html = output_dir / "documentation.madoc.html"
    assert output_html.is_file()

    html = output_html.read_text(encoding="utf-8")
    assert 'onclick="display(1)"' in html
    assert 'download="madoc_sources.zip"' in html

    # In no_b64 mode the archive link should be a filesystem relative path, not a data URI.
    assert "data:application/zip;base64" not in html
    assert "../src/madoc_sources.zip" in html

    archive = source_dir / "madoc_sources.zip"
    assert archive.is_file()


def test_main_uses_custom_css_file(tmp_path: Path) -> None:
    source_dir = tmp_path / "src"
    output_dir = tmp_path / "out"
    source_dir.mkdir()
    output_dir.mkdir()

    (source_dir / "(01)alpha.md").write_text("# Alpha", encoding="utf-8")
    custom_css = tmp_path / "custom.css"
    custom_css.write_text("/* custom-css-marker */\nbody { color: rgb(1, 2, 3); }", encoding="utf-8")

    generate_main(
        source_dir=str(source_dir),
        output_dir=str(output_dir),
        title="Test",
        css_file=str(custom_css),
    )

    html = (output_dir / "documentation.madoc.html").read_text(encoding="utf-8")
    assert "custom-css-marker" in html


def test_cmd_get_css_copies_default_css(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()

    monkeypatch.setattr(sys, "argv", ["madoc", "--get-css", str(source_dir)])
    madoc_cmd()

    copied_css = source_dir / "madoc_style.css"
    assert copied_css.is_file()
    assert copied_css.read_text(encoding="utf-8")


def test_cmd_add_src_with_css_adds_css_and_build_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    (source_dir / "(01)alpha.md").write_text("# Alpha", encoding="utf-8")

    custom_css = tmp_path / "custom.css"
    custom_css.write_text("body { color: red; }", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "madoc",
            "--add-src",
            "--no-b64",
            "--css",
            str(custom_css),
            str(source_dir),
        ],
    )
    madoc_cmd()

    build_script = source_dir / "madoc_build.sh"
    assert build_script.is_file()
    build_script_content = build_script.read_text(encoding="utf-8")
    assert "--css \"custom.css\"" in build_script_content

    archive = source_dir / "madoc_sources.zip"
    assert archive.is_file()
    with zipfile.ZipFile(archive, "r") as zf:
        assert "custom.css" in zf.namelist()
