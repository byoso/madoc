#! /usr/bin/env python3
# coding: utf-8

import os
import json
import uuid
import argparse

from jinja2 import Environment, select_autoescape

from madoc.loader import MadocLoader


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.getcwd()

env = Environment(
    loader=MadocLoader(os.path.join(BASE_DIR, "templates")),
    autoescape=select_autoescape()
)

template = env.get_template("madoc/render.html")


def cmd(*args, **kwargs):
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Convert all markdown files in the directory into a single html file")
    parser.add_argument("--bg-color", type=str, default="#fbfbfb", help="Background color, default is #fbfbfb")
    parser.add_argument("--title", type=str, default="Documents", help="Title of the page, default is 'Documents'")
    args = parser.parse_args()

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
