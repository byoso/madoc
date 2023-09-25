#! /usr/bin/env python3
# coding: utf-8

import os
import json
import uuid

from jinja2 import Environment, select_autoescape, PackageLoader


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.getcwd()


env = Environment(
    loader=PackageLoader("templates", "madoc"),
    autoescape=select_autoescape()
)

template = env.get_template("render.html")


def md_to_html(
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

    template = env.get_template("render.html")
    context = {
        "uuid": uuid_value,
        "bg_color": bg_color,
        "title": title,
        "pages": json_pages,
    }

    with open("documentation.madoc.html", "w") as f:
        f.write(template.render(**context))

    print("Done !")


def cmd():
    """Command line interface"""
    md_to_html()


if __name__ == "__main__":
    md_to_html()
