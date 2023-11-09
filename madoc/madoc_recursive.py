import os
import uuid
import json
from pprint import pprint
import shutil
from datetime import date

from jinja2 import Environment, select_autoescape

from madoc.loader import MadocLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.getcwd()

env = Environment(
    loader=MadocLoader(os.path.join(BASE_DIR, "templates")),
    autoescape=select_autoescape()
)


def build_html(path, pages, links, dist_dir, level, bg_color, no_mark, title):
    """Convert all markdown files to html files"""
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
        "index_link": level*"../" + "index.html",
        "favicon_url": level*"../" + "favicon.ico",
        "links": links,
        "bg_color": bg_color,
        "no_mark": no_mark,
        "title": title,
        "pages": json_pages,
    }

    with open(os.path.join(dist_dir, "documentation.madoc.html"), "w") as f:
        f.write(template.render(**context))


def parser(directory=DIR, bg_color="#fbfbfb", no_mark=False, dist_dir="madoc_dist", level=0):
    datas = { 'id': str(uuid.uuid4()), 'directory': directory, 'subdirs': [], 'files': [], 'foldable': True}
    is_valid = False
    links = []
    for name in os.listdir(directory):
        if name.startswith("."):
            continue

        path = os.path.join(directory, name)
        # Directories
        if os.path.isdir(path):
            rec_datas, rec_is_valid = parser(directory=path, bg_color=bg_color, no_mark=no_mark, dist_dir=os.path.join(dist_dir, name), level=level+1)
            if rec_is_valid:
                links = [{
                    'name': link['directory'].split("/")[-1],
                    'url':"/".join(link['directory'].split("/")[-(rec_datas['level']-level):]) + "/documentation.madoc.html"
                    } for link in rec_datas['subdirs']]
                datas['subdirs'].append(rec_datas)
                # pprint(datas)
                # makes the tree in madoc_dist
                if not os.path.exists(os.path.join(dist_dir, name)):
                    os.makedirs(os.path.join(dist_dir, name))
                # sort rec_datas['files'] by name
                rec_datas['files'] = sorted(rec_datas['files'])
                if not rec_datas['files']:
                    rec_datas['foldable'] = False
                build_html(
                    path=path,
                    pages=rec_datas['files'],
                    links=links,
                    dist_dir=os.path.join(dist_dir, name),
                    level=level+1,
                    bg_color=bg_color,
                    no_mark=no_mark,
                    title=name,
                )
                is_valid = True
        # files
        elif name.endswith(".md"):
            is_valid = True
            datas['files'].append(name)
        # copy or ignore files
        elif name.endswith(".madoc.html"):
            continue
        elif name.split(".")[-1] in ["html", "css", "js", "png", "jpg", "jpeg", "gif", "svg", "ico", "json"]:
            if not os.path.exists(os.path.join(dist_dir)):
                os.makedirs(os.path.join(dist_dir))
            shutil.copyfile(path, os.path.join(dist_dir, name))
        datas['level'] = level
    return datas, is_valid


def index_builder(datas, bg_color="#fbfbfb", no_mark=False, title=""):
    date_created = date.today().strftime("%B %d, %Y")
    template = env.get_template("madoc/recursive_index.html")
    datas = [datas]
    # pprint(datas)
    context = {
        "bg_color": bg_color,
        "no_mark": no_mark,
        "datas": datas,
        "base_dir": "",
        "date_created": date_created,
        "title": title,
    }

    with open(os.path.join(DIR, 'madoc_dist', "index.html"), "w") as f:
        f.write(template.render(**context))


def main_recursive(
    bg_color="#fbfbfb",
    no_mark=False,
    title="",
):
    # delete existant madoc_dist folder
    if os.path.exists(os.path.join(DIR, "madoc_dist")):
        shutil.rmtree(os.path.join(DIR, "madoc_dist"))

    # Initialize the loop
    rec_datas, rec_is_valid = parser(directory=DIR, bg_color=bg_color, no_mark=no_mark, dist_dir=os.path.join(DIR, "madoc_dist"))

    if not rec_datas['files']:
        rec_datas['foldable'] = False

    if rec_is_valid:
        links = [{
            'name': link['directory'].split("/")[-1],
            'url':link['directory'].split("/")[-1] + "/documentation.madoc.html"
            } for link in rec_datas['subdirs']]
        datas = {'subdirs': [], 'files': []}
        datas['subdirs'].append(rec_datas)
        datas['id'] = uuid.uuid4()
        datas['foldable'] = True
        # pprint(datas)
        # sort rec_datas['files'] by name
        rec_datas['files'] = sorted(rec_datas['files'])
        build_html(
            path=DIR,
            pages=rec_datas['files'],
            links=links,
            dist_dir=os.path.join(DIR, "madoc_dist"),
            level=0,
            bg_color=bg_color,
            no_mark=no_mark,
            title=title,
        )
    # print("=== main DIR: ", DIR)
    # pprint(rec_datas)
    index_builder(rec_datas, bg_color=bg_color, no_mark=no_mark, title=title)

    # copy the default favicon if none exists
    if not os.path.exists(os.path.join(DIR, "favicon.ico")):
        shutil.copy(
            os.path.join(BASE_DIR, "assets", "favicon.ico"),
            os.path.join(DIR, 'madoc_dist', "favicon.ico")
            )
    print("Madoc SUCCESS: recursive build done ! Check the 'madoc_dist' folder.")
