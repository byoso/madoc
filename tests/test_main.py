from pathlib import Path

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
