#! /usr/bin/env python3
# coding: utf-8

import os
import re
import argparse

from jinja2 import Environment, select_autoescape
import markdown

from madoc.loader import MadocLoader
from madoc import __version__
from madoc.base64_converter import convert_images_to_base64
from madoc.silly_engine.text_tools import c

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.getcwd()

# defaults
no_b64 = False

env = Environment(
    loader=MadocLoader(os.path.join(BASE_DIR, "templates")),
    autoescape=select_autoescape()
)

template = env.get_template("madoc/render.html")


def cmd(*args, **kwargs) -> None:
    """Command line interface"""
    # positionnal arguments
    parser = argparse.ArgumentParser(
        description=(
            "Convert all markdown files in the directory into a single html file. "
            "\nUse parenthesis suffix in the names your files to sort them (e.g: '(01)introduction.md')"
            "\nOr recursively gather your documentation in an index.html file and subfolders, usable as a static site."
            )
        )
    parser.add_argument("--no-b64", help="do not convert files to base64", action="store_true")
    parser.add_argument("-t", "--title", type=str, default="Documents", help="Title of the page, default is 'Documents'")
    parser.add_argument("-c", "--code", help="enable code syntax coloration", action="store_true")
    parser.add_argument("-V", "--version", help="Version", action="store_true")
    args = parser.parse_args()
    no_mark = False
    if args.version:
        print(__version__)
        return
    if args.code:
        print("= syntax coloring enabled")
    if args.no_b64:
        no_b64 = True
        print("= no b64 images")
        minimize_htlm = True

    main(title=args.title, syntax_color=args.code)


def clean_filename(filename: str) -> str:
    return re.sub(r"^\([^)]+\)", "", filename).strip().replace(".md", "").replace(".MD", "")

def main(
    title="Documents",
    syntax_color=False
) -> None:
    """Convert all markdown files to html files"""
    pages = []
    files = sorted(os.listdir(DIR))
    for file in files:
        page = {}
        if file.endswith(".md") or file.endswith(".MD"):
            print(file)
            with open(file, "r") as md_file:
                page['name'] = clean_filename(file)
                raw_content = md_file.read()
                extentions = [
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
                    "wikilinks",         # Wiki-style links])
                ]
                if syntax_color:
                    extentions.append("codehilite")  # Syntax highlighting (requires Pygments))
                page["content"] = markdown.markdown(raw_content, extensions=extentions)
                if not no_b64:
                    page["content"] = convert_images_to_base64(page["content"])
            pages.append(page)

    context = {
        "title": title,
        "pages": pages,
        "css_style": "madoc/madoc_style.css"
    }

    html_content = template.render(**context)
    with open("documentation.madoc.html", "w") as f:
        f.write(html_content)

    print(f"{c.success}Done !{c.end}")


if __name__ == "__main__":
    cmd()
