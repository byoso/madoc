#! /usr/bin/env python3
# coding: utf-8

import os
import json
import uuid
import argparse

from jinja2 import Environment, select_autoescape

from madoc.loader import MadocLoader
from madoc import __version__
from madoc.madoc_recursive import main_recursive

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.getcwd()

env = Environment(
    loader=MadocLoader(os.path.join(BASE_DIR, "templates")),
    autoescape=select_autoescape()
)

template = env.get_template("madoc/render.html")


def cmd(*args, **kwargs):
    """Command line interface"""
    # positionnal arguments
    parser = argparse.ArgumentParser(description="Convert all markdown files in the directory into a single html file")
    parser.add_argument("-b", "--bg-color", type=str, default="#fbfbfb", help="Background color, default is #fbfbfb")
    parser.add_argument("-t", "--title", type=str, default="Documents", help="Title of the page, default is 'Documents', non recursive only")
    # flags (store_true)
    parser.add_argument("-v", "--version", help="Version", action="store_true")
    parser.add_argument("-r", help="Recursive action, links the subfolders to an index", action="store_true")
    args = parser.parse_args()
    if args.version:
        print(__version__)
        return
    if args.r:
        main_recursive(args.bg_color)
        return
    main(args.bg_color, args.title)


def main(
    bg_color="#fbfbfb",
    title="Documents",
):
    """Convert all markdown files to html files"""
    pages = []
    uuid_value = str(uuid.uuid4())
    for file in os.listdir(DIR):
        page = {}
        if file.endswith(".md"):
            with open(file, "r") as md_file:
                page['content'] = md_file.read().replace("<", f"<{uuid_value}").replace(">", f"{uuid_value}>")
                page['name'] = file.replace(".md", "")
                pages.append(page)
    json_pages = json.dumps(pages)

    context = {
        "uuid": uuid_value,
        "bg_color": bg_color,
        "title": title,
        "pages": json_pages,
    }

    with open("documentation.madoc.html", "w") as f:
        f.write(template.render(**context))

    print("Done !")


if __name__ == "__main__":
    cmd()
