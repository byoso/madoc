#! /usr/bin/env python3
# coding: utf-8

import os
import re
import argparse
import base64
import shutil

from jinja2 import Environment, FileSystemLoader, ChoiceLoader, select_autoescape
import markdown

from madoc.loader import MadocLoader
from madoc.utils import create_zip_from_files, extract_local_resource_paths
from madoc import __version__
from madoc.base64_converter import convert_images_to_base64
from madoc.silly_engine.text_tools import c

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_madoc_loader = MadocLoader(os.path.join(BASE_DIR, "templates"))
env = Environment(
    loader=_madoc_loader,
    autoescape=select_autoescape()
)

template = env.get_template("madoc/render.html")


def cmd(*args, **kwargs) -> None:
    """Command line interface"""
    # positionnal arguments
    parser = argparse.ArgumentParser(
        description=(
            "Convert all markdown files in a source directory into a single html file. "
            "\nUse parenthesis suffix in the names your files to sort them (e.g: '(01)introduction.md')"
            "\nOr recursively gather your documentation in an index.html file and subfolders, usable as a static site."
            "\n For madoc-bookbinding, see the help with madoc-bb -h"
            )
        )
    parser.add_argument("source", nargs="?", default=".", help="source directory containing markdown files (default: current directory)")
    parser.add_argument("-o", "--output", dest="output_dir", type=str, default=None, help="output directory for generated html (relative to launch directory)")
    parser.add_argument("--no-b64", help="do not convert files to base64", action="store_true")
    parser.add_argument("--add-src", help="includes scr files, at the cost of doubling the size of the document", action="store_true")
    parser.add_argument("--get-template", help="get a madoc_template.html in source directory and exit", action="store_true")
    parser.add_argument("-f", "--template", dest="template_file", type=str, default=None, help="path to alternate Jinja2 template")
    parser.add_argument("-t", "--title", type=str, default="Documents", help="Title of the page, default is 'Documents'")
    parser.add_argument("-c", "--code", help="enable code syntax coloration", action="store_true")
    parser.add_argument("-V", "--version", help="Version", action="store_true")
    args = parser.parse_args()
    launch_dir = os.getcwd()
    source_dir = os.path.abspath(args.source)
    if not os.path.isdir(source_dir):
        print(f"Source directory not found: {source_dir}")
        return

    if args.output_dir:
        output_dir = args.output_dir
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(launch_dir, output_dir)
        output_dir = os.path.abspath(output_dir)
    else:
        output_dir = source_dir

    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"Cannot create output directory: {output_dir} ({e})")
        return

    if args.get_template:
        src_template = os.path.join(BASE_DIR, "templates", "madoc", "render.html")
        dest_template = os.path.join(source_dir, "madoc_template.html")
        try:
            shutil.copyfile(src_template, dest_template)
            print(f"Copied template to {dest_template}")
        except OSError as e:
            print(f"Error copying template: {e}")
        return

    if args.template_file:
        template_candidate = args.template_file
        if not os.path.isabs(template_candidate):
            template_candidate = os.path.join(source_dir, template_candidate)
        if not os.path.isfile(template_candidate):
            print(f"Template file not found: {template_candidate}")
            return
        args.template_file = template_candidate

    no_b64 = False
    add_src = False
    if args.version:
        print(__version__)
        return
    if args.code:
        print("= syntax coloring enabled")
    if args.no_b64:
        no_b64 = True
        print("= no b64 images")
    if args.add_src:
        add_src = True

    # Command line reconstruction for build script
    def q(value: str) -> str:
        # Quote argument in double-quotes; escape existing quotes and backslashes
        value = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{value}"'

    command_parts = ["madoc"]
    if args.title:
        command_parts.extend(["-t", q(args.title)])
    if args.code:
        command_parts.append("--code")
    if args.no_b64:
        command_parts.append("--no-b64")
    if args.add_src:
        command_parts.append("--add-src")
    if args.output_dir:
        command_parts.extend(["-o", q(args.output_dir)])
    command_parts.append(q(args.source))

    template_basename = None
    if args.template_file:
        template_basename = os.path.basename(args.template_file)
        command_parts.extend(["-f", q(template_basename)])

    build_command = " ".join(command_parts)

    main(
        source_dir=source_dir,
        output_dir=output_dir,
        title=args.title,
        syntax_color=args.code,
        add_src=add_src,
        no_b64=no_b64,
        template_file=args.template_file,
        template_basename=template_basename,
        build_command=build_command,
    )


def clean_filename(filename: str) -> str:
    return re.sub(r"^\([^)]+\)", "", filename).strip().replace(".md", "").replace(".MD", "")


def rewrite_internal_md_links(html: str, file_to_tab_index: dict) -> str:
    """Replace internal .md href links with JS tab navigation calls."""
    def replace(match):
        quote = match.group(1)
        href = match.group(2)
        clean = href.split("#")[0].split("?")[0].strip()
        if clean in file_to_tab_index:
            idx = file_to_tab_index[clean]
            return f'href={quote}javascript:void(0){quote} onclick="display({idx})"'
        return match.group(0)
    return re.sub(r'href=(["\'])([^"\']+)\1', replace, html)

def main(
    source_dir: str = ".",
    output_dir: str | None = None,
    title: str="Documents",
    syntax_color: bool=False,
    add_src: bool = False,
    no_b64: bool = False,
    template_file: str | None = None,
    template_basename: str | None = None,
    build_command: str | None = None,
) -> None:
    """Convert all markdown files to html files"""
    source_dir = os.path.abspath(source_dir)
    output_dir = os.path.abspath(output_dir or source_dir)
    pages = []
    files = sorted(os.listdir(source_dir))
    md_files_sorted = [f for f in files if f.endswith(".md") or f.endswith(".MD")]
    file_to_tab_index = {f: i + 1 for i, f in enumerate(md_files_sorted)}
    source_files = []
    linked_resources = set()
    for file in files:
        page = {}
        if file.endswith(".md") or file.endswith(".MD"):
            print(file)
            source_file_path = os.path.join(source_dir, file)
            source_files.append(source_file_path)
            with open(source_file_path, "r", encoding="utf-8") as md_file:
                page['name'] = clean_filename(file)
                raw_content = md_file.read()
                linked_resources.update(extract_local_resource_paths(raw_content, base_dir=source_dir))
                extensions = [
                    "abbr",              # Abbreviations
                    "admonition",        # Notes, Warnings, etc.
                    "attr_list",         # HTML attributes on elements
                    "def_list",          # Definition lists
                    "fenced_code",       # Triple-backtick code blocks
                    "footnotes",         # Footnotes
                    "legacy_attrs",      # Support for legacy attributes
                    "legacy_em",         # Legacy emphasis handling
                    "md_in_html",        # Markdown inside raw HTML blocks
                    "meta",              # YAML-style metadata
                    "nl2br",             # Newline to <br> conversion
                    "sane_lists",        # Better list handling
                    "smarty",            # Smart punctuation (quotes, dashes)
                    "tables",            # GitHub-style tables
                    "toc",               # Table of Contents
                    "wikilinks",         # Wiki-style links
                ]
                if syntax_color:
                    extensions.append("codehilite")  # Syntax highlighting (requires Pygments)
                page["content"] = markdown.markdown(raw_content, extensions=extensions)
                page["content"] = rewrite_internal_md_links(page["content"], file_to_tab_index)
                if not no_b64:
                    page["content"] = convert_images_to_base64(page["content"])
            pages.append(page)

    source_files_zip = None

    if add_src:
        linked_resources = set()
        for source_file in source_files:
            try:
                with open(source_file, "r", encoding="utf-8") as md_file:
                    linked_resources.update(extract_local_resource_paths(md_file.read(), base_dir=source_dir))
            except FileNotFoundError:
                continue

        extras = sorted(linked_resources - set(source_files))

        # Add template file itself among sources so we can rebuild exactly
        if template_file and template_basename:
            template_path_abs = os.path.abspath(template_file)
            local_template_path = os.path.join(source_dir, template_basename)
            try:
                if os.path.isfile(template_path_abs):
                    if template_path_abs != os.path.abspath(local_template_path):
                        # copy template into current working directory (zip root) as basename
                        shutil.copyfile(template_path_abs, local_template_path)
                    # always include the basename in archive sources
                    extras.append(local_template_path)
            except OSError as e:
                print(f"Warning: could not include template in archive: {e}")

        # add madoc_build.sh in archive with exact invocation command used
        if build_command:
            build_script_path = os.path.join(source_dir, "madoc_build.sh")
            try:
                with open(build_script_path, "w", encoding="utf-8") as f:
                    f.write("#! /bin/bash\n\n")
                    f.write(build_command + "\n")
                os.chmod(build_script_path, 0o755)
                extras.append(build_script_path)
            except OSError as e:
                print(f"Warning: could not create build script: {e}")

        archive_path = create_zip_from_files(
            source_files,
            extra_files=extras,
            output_dir=source_dir,
            base_dir=source_dir,
        )

        if archive_path:
            if not no_b64:
                with open(archive_path, "rb") as archive_file:
                    archive_b64 = base64.b64encode(archive_file.read()).decode("ascii")
                    source_files_zip = f"data:application/zip;base64,{archive_b64}"
            else:
                source_files_zip = os.path.relpath(archive_path, start=output_dir)

    # Template selection
    if template_file:
        template_path = template_file
        if not os.path.isabs(template_path):
            template_path = os.path.join(source_dir, template_path)
        template_path = os.path.abspath(template_path)
        if not os.path.isfile(template_path):
            print(f"Template file not found: {template_path}")
            return
        custom_env = Environment(
            loader=ChoiceLoader([
                FileSystemLoader(os.path.dirname(template_path)),
                _madoc_loader,
            ]),
            autoescape=select_autoescape()
        )
        template_to_use = custom_env.get_template(os.path.basename(template_path))
    else:
        template_to_use = template

    context = {
        "title": title,
        "pages": pages,
        "css_style": "madoc/madoc_style.css",
        "has_source_files": add_src,
        "source_files_zip": source_files_zip,
    }

    html_content = template_to_use.render(**context)
    output_file = os.path.join(output_dir, "documentation.madoc.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"{c.success}Done !{c.end}")


if __name__ == "__main__":
    cmd()
