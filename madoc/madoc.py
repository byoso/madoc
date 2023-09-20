#! /usr/bin/env python3
# coding: utf-8

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DIR = os.getcwd()
with open(os.path.join(BASE_DIR, 'templates', 'start.html.tpl'), 'r') as start:
    START = start.read()
with open(os.path.join(BASE_DIR, 'templates', 'end.html.tpl'), 'r') as end:
    END = end.read()


def md_to_html():
    """Convert all markdown files to html files"""
    pages = []
    for file in os.listdir(DIR):
        page = {}
        if file.endswith(".md"):
            with open(file, "r") as md_file:
                page['content'] = md_file.read().replace("<", "&lt;").replace(">", "&gt;")
                page['name'] = file.replace(".md", "")
                pages.append(page)

    json_pages = json.dumps(pages)
    with open(os.path.join(DIR, "documentation_from_md.html"), "w") as html_file:
        html_file.write(START)
        html_file.write(json_pages)
        html_file.write(END)


def cmd():
    """Command line interface"""
    md_to_html()


if __name__ == "__main__":
    md_to_html()