#! /usr/bin/env python3

import argparse
import base64
import mimetypes
import os
import re
import shutil

import requests
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, select_autoescape

from madoc import __version__
from madoc.loader import MadocLoader
from madoc.silly_engine.text_tools import c

PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_NAME = "madoc/bookbinding.html"
DEFAULT_TEMPLATE_COPY_NAME = "madoc_bookbinding_template.html"
DEFAULT_CSS_COPY_NAME = "madoc_style.css"

_madoc_loader = MadocLoader(os.path.join(PACKAGE_DIR, "templates"))
env = Environment(
    loader=_madoc_loader,
    autoescape=select_autoescape(),
)


class OrderedPathAction(argparse.Action):
    """Preserve user order for chained -p/-i options."""

    def __call__(self, parser, namespace, values, option_string=None):
        chain = getattr(namespace, self.dest, None)
        if chain is None:
            chain = []
            setattr(namespace, self.dest, chain)

        kind = "page" if option_string in ("-p", "--page") else "icon"
        chain.append((kind, values))


def _is_remote(path: str) -> bool:
    return path.startswith(("http://", "https://"))


def _is_data_uri(path: str) -> bool:
    return path.startswith("data:")


def _normalize_href(path: str) -> str:
    return path.replace(os.sep, "/")


def _extract_title(html_text: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    raw = re.sub(r"\s+", " ", match.group(1)).strip()
    return raw or None


def _read_local_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _read_local_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _fetch_remote_text(url: str) -> str:
    response = requests.get(url, timeout=8)
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"
    return response.text


def _fetch_remote_bytes(url: str) -> tuple[bytes, str]:
    response = requests.get(url, timeout=8)
    response.raise_for_status()
    mime = response.headers.get("Content-Type", "application/octet-stream").split(";")[0].strip()
    return response.content, mime


def _build_page_url(path: str, output_dir: str, no_b64: bool) -> str:
    if _is_data_uri(path):
        return path

    if no_b64:
        if _is_remote(path):
            return path
        return _normalize_href(os.path.relpath(path, start=output_dir))

    if _is_remote(path):
        html_text = _fetch_remote_text(path)
        return f"data:text/html;base64,{base64.b64encode(html_text.encode('utf-8')).decode('ascii')}"

    html_bytes = _read_local_bytes(path)
    return f"data:text/html;base64,{base64.b64encode(html_bytes).decode('ascii')}"


def _build_icon_url(path: str, output_dir: str, no_b64: bool) -> str:
    if _is_data_uri(path):
        return path

    if no_b64:
        if _is_remote(path):
            return path
        return _normalize_href(os.path.relpath(path, start=output_dir))

    if _is_remote(path):
        data, mime = _fetch_remote_bytes(path)
    else:
        data = _read_local_bytes(path)
        mime, _ = mimetypes.guess_type(path)
        if not mime:
            mime = "application/octet-stream"

    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _resolve_page_label(path: str) -> str:
    if _is_remote(path):
        try:
            title = _extract_title(_fetch_remote_text(path))
            if title:
                return title
        except requests.RequestException:
            pass
        return path

    if _is_data_uri(path):
        return "Embedded page"

    try:
        title = _extract_title(_read_local_text(path))
        if title:
            return title
    except OSError:
        pass
    return os.path.splitext(os.path.basename(path))[0]


def _prepare_ordered_entries(chain: list[tuple[str, str]], launch_dir: str) -> list[dict]:
    entries: list[dict] = []

    for kind, raw_value in chain:
        value = raw_value.strip()

        if kind == "page":
            if not value:
                raise ValueError("Empty page path is not allowed")

            resolved = value
            if not (_is_remote(value) or _is_data_uri(value) or os.path.isabs(value)):
                resolved = os.path.abspath(os.path.join(launch_dir, value))

            if not (_is_remote(resolved) or _is_data_uri(resolved)) and not os.path.isfile(resolved):
                raise FileNotFoundError(f"Page file not found: {resolved}")

            entries.append({"page": resolved, "icon": None})
            continue

        if not entries:
            raise ValueError("Option -i/--icon must come after a -p/--page option")

        resolved_icon = value
        if not (_is_remote(value) or _is_data_uri(value) or os.path.isabs(value)):
            resolved_icon = os.path.abspath(os.path.join(launch_dir, value))

        if not (_is_remote(resolved_icon) or _is_data_uri(resolved_icon)) and not os.path.isfile(resolved_icon):
            raise FileNotFoundError(f"Icon file not found: {resolved_icon}")

        entries[-1]["icon"] = resolved_icon

    return entries


def cmd(*args, **kwargs) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a single HTML portal from multiple existing HTML pages. "
            "Chain -p/--page and -i/--icon options in order."
        )
    )
    parser.add_argument("-p", "--page", dest="chain", action=OrderedPathAction, metavar="PATH")
    parser.add_argument("-i", "--icon", dest="chain", action=OrderedPathAction, metavar="PATH")
    parser.add_argument("--no-b64", help="do not convert pages/icons to base64", action="store_true")
    parser.add_argument("-o", "--output", dest="output_dir", type=str, default=".", help="output directory (relative to launch directory)")
    parser.add_argument("-f", "--template", dest="template_file", type=str, default=None, help="path to alternate Jinja2 template")
    parser.add_argument("--css", dest="css_file", type=str, default=None, help="path to alternate CSS file")
    parser.add_argument("-t", "--title", type=str, default="Bookbinding", help="title of the page")
    parser.add_argument("--get-template", help="copy a madoc bookbinding template in current directory and exit", action="store_true")
    parser.add_argument("--get-css", help="copy a madoc css style in current directory and exit", action="store_true")
    parser.add_argument("-V", "--version", help="Version", action="store_true")
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    launch_dir = os.getcwd()
    output_dir = args.output_dir
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(launch_dir, output_dir)
    output_dir = os.path.abspath(output_dir)

    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"Cannot create output directory: {output_dir} ({e})")
        return

    copied_asset = False
    if args.get_template:
        src_template = os.path.join(PACKAGE_DIR, "templates", "madoc", "bookbinding.html")
        dest_template = os.path.join(launch_dir, DEFAULT_TEMPLATE_COPY_NAME)
        try:
            shutil.copyfile(src_template, dest_template)
            print(f"Copied template to {dest_template}")
            copied_asset = True
        except OSError as e:
            print(f"Error copying template: {e}")
    if args.get_css:
        src_css = os.path.join(PACKAGE_DIR, "templates", "madoc", "madoc_style.css")
        dest_css = os.path.join(launch_dir, DEFAULT_CSS_COPY_NAME)
        try:
            shutil.copyfile(src_css, dest_css)
            print(f"Copied css to {dest_css}")
            copied_asset = True
        except OSError as e:
            print(f"Error copying css: {e}")
    if copied_asset:
        return

    css_path = None
    if args.css_file:
        css_path = args.css_file
        if not os.path.isabs(css_path):
            css_path = os.path.join(launch_dir, css_path)
        css_path = os.path.abspath(css_path)
        if not os.path.isfile(css_path):
            print(f"CSS file not found: {css_path}")
            return

    chain = args.chain or []
    if not chain:
        parser.error("No pages provided. Use -p/--page at least once.")

    try:
        raw_entries = _prepare_ordered_entries(chain, launch_dir)
    except (ValueError, FileNotFoundError) as e:
        parser.error(str(e))

    items = []
    for entry in raw_entries:
        try:
            page_url = _build_page_url(entry["page"], output_dir=output_dir, no_b64=args.no_b64)
            icon_url = None
            if entry["icon"]:
                icon_url = _build_icon_url(entry["icon"], output_dir=output_dir, no_b64=args.no_b64)
            title = _resolve_page_label(entry["page"])
            items.append({
                "title": title,
                "page_url": page_url,
                "icon_url": icon_url,
            })
        except (OSError, requests.RequestException) as e:
            print(f"Error while processing '{entry['page']}': {e}")
            return

    if args.template_file or css_path:
        loader_dirs = []

        template_path = None
        if args.template_file:
            template_path = args.template_file
            if not os.path.isabs(template_path):
                template_path = os.path.join(launch_dir, template_path)
            template_path = os.path.abspath(template_path)

            if not os.path.isfile(template_path):
                print(f"Template file not found: {template_path}")
                return
            loader_dirs.append(os.path.dirname(template_path))

        if css_path:
            css_dir = os.path.dirname(css_path)
            if css_dir not in loader_dirs:
                loader_dirs.append(css_dir)

        custom_env = Environment(
            loader=ChoiceLoader([
                *(FileSystemLoader(path) for path in loader_dirs),
                _madoc_loader,
            ]),
            autoescape=select_autoescape(),
        )

        if template_path:
            template_to_use = custom_env.get_template(os.path.basename(template_path))
        else:
            template_to_use = custom_env.get_template(TEMPLATE_NAME)
    else:
        template_to_use = env.get_template(TEMPLATE_NAME)

    css_style = "madoc/madoc_style.css"
    if css_path:
        css_style = os.path.basename(css_path)

    html_content = template_to_use.render(
        title=args.title,
        items=items,
        css_style=css_style,
    )

    output_file = os.path.join(output_dir, "madoc-bookbinding.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"{c.success}Done !{c.end}")
