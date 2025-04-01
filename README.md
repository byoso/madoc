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

Open a terminal in the directory where the .md files are,
and just type:

`madoc`

done, you have your documentation in a single html file.

Know more options with `madoc -h`.


# Changelog

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
