import os
import uuid
import json
from pprint import pprint
import shutil

from jinja2 import Environment, select_autoescape

from madoc.loader import MadocLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.getcwd()

env = Environment(
    loader=MadocLoader(os.path.join(BASE_DIR, "templates")),
    autoescape=select_autoescape()
)


def build_html(path, pages, links, dist_dir, level, bg_color, title):
    """Convert all markdown files to html files"""
    print("===links: ", links)
    template = env.get_template("madoc/recursive_render.html")
    pages = []
    uuid_value = str(uuid.uuid4())
    for file in os.listdir(path):
        page = {}
        if file.endswith(".md"):
            with open(os.path.join(path, file), "r") as md_file:
                page['content'] = md_file.read().replace("<", f"<{uuid_value}").replace(">", f"{uuid_value}>")
                page['name'] = file.replace(".md", "")
                pages.append(page)
    json_pages = json.dumps(pages)

    context = {
        "uuid": uuid_value,
        "bg_color": bg_color,
        "index_link": level*"../" + "index.html",
        "links": links,
        "title": title,
        "pages": json_pages,
    }

    with open(os.path.join(dist_dir, "documentation.madoc.html"), "w") as f:
        f.write(template.render(**context))


def parser(directory=DIR, dist_dir="madoc_dist", level=0):
    datas = {'directory': directory, 'subdirs': [], 'files': []}
    is_valid = False
    for name in os.listdir(directory):
        if name.startswith("."):
            continue

        path = os.path.join(directory, name)
        # Directories
        if os.path.isdir(path):
            rec_datas, rec_is_valid = parser(directory=path, dist_dir=os.path.join(dist_dir, name), level=level+1)
            if rec_is_valid:
                datas['subdirs'].append(rec_datas)
                print("=== subdirs: ")
                pprint(rec_datas['subdirs'])
                # makes the tree in madoc_dist
                if not os.path.exists(os.path.join(dist_dir, name)):
                    os.makedirs(os.path.join(dist_dir, name))
                    links = []
                    for elem in datas['subdirs']:
                        links.append({'name': elem['directory'].split("/")[-1]})
                        # links.append({'name': "test"})
                    build_html(
                        path=path,
                        pages=rec_datas['files'],
                        links=links,
                        dist_dir=os.path.join(dist_dir, name),
                        level=level+1,
                        bg_color="#fbfbfb",
                        title="Documents",
                    )
                is_valid = True
        # files
        elif name.endswith(".md"):
            is_valid = True
            datas['files'].append(name)
    return datas, is_valid


def index_builder(datas, bg_color="#fbfbfb", title="Documents"):
    pass


def main_recursive(
    bg_color="#fbfbfb",
    title="Documents",
):
    print("=== main DIR: ", DIR)
    if os.path.exists(os.path.join(DIR, "madoc_dist")):
        shutil.rmtree(os.path.join(DIR, "madoc_dist"))
    datas, _validity = parser(directory=DIR, dist_dir=os.path.join(DIR, "madoc_dist"))
    pprint(datas)
    index_builder(datas, bg_color=bg_color, title=title)
