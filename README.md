# Madoc


## What is Madoc for ?

It is a terminal tool to automatically generate a single html documentation file from all
the .md files found in the directory.

Cool stuff to join a clean and easy to read documentation to some project.


# Installation

```console
pip install madoc
```


# Usage

Use the source directory as a positional argument:

`madoc .`

You can combine options and source path:

`madoc -t "My title" .`

You can also choose where the generated html is written with `-o`/`--output`
(path is relative to where you launch the command):

`madoc test_files -o out`

`madoc -t "My title" test_files -o ./dist`

If no source directory is provided, Madoc uses the current directory:

`madoc`

done, you have your documentation in a single html file in the source directory.

If `-o` is provided, the html file is written in the output directory instead.

Know more options with `madoc -h`.


# Bookbinding usage

You can aggregate multiple existing html pages into a single portal page with:

`madoc-bookbinding`

Short alias:

`madoc-bb`

Examples:

`madoc-bb -p some.html -i icon.png -p another.html --output .`

`madoc-bookbinding -p first.html -p second.html -o ./dist`

Notes:
- `-p` adds a page.
- `-i` sets the icon of the previous `-p`.
- default mode embeds pages/icons as base64.
- `--no-b64` keeps file links/URLs.
- `--get-template` copies the default bookbinding template locally.


# Changelog

- 1.5.0: css overload ability
- 1.4.0: Bookdinding
- 1.3.0: customizing a template is possible
- 1.2.6: converts download links to base64 (optionnal)
- 1.2.5: responsive design improved, possibility to prefix the files with '(XXX..)' to sort the files without appearing in the displayed names
- 1.2.0: reworked without any JS dependencies (=readable offline), prettier template, base64 images conversion !
    - to be deprecated: the recursive option, will be replaced by something else (WIP...)
- 1.1.1: responsive design
- 1.1.0: Recursive build mode

# Libraries used by Madoc
JS  (used in recursive mode only)
- Bulma (CSS framework)
- Vue.js (JS framework)
- Marked (JS library)

Python (already included in the pip setup)
- Jinja2 (python library)
- markdown
- Pygments
- requests
