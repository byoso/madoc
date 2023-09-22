#! /usr/bin/env python3
# coding: utf-8

import os
import json
import uuid

import jinja2

from jinja2 import Environment, select_autoescape, PackageLoader, FileSystemLoader


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.getcwd()
TEMPLATES = os.path.join(BASE_DIR, "templates")
print("=== templates: ", TEMPLATES)

env = Environment(
    # loader=PackageLoader("templates", "madoc"),
    loader=FileSystemLoader(TEMPLATES),
    autoescape=select_autoescape()
)

template = env.get_template("render.html")



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
    main()


if __name__ == "__main__":
    main()
