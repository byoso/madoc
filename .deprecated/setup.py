# #! /usr/bin/env python3
# # coding: utf-8

# """
# REMINDER:
# 1- build
# ./setup.py sdist bdist_wheel
# 2- basic verifications
# twine check dist/*
# 2.5- Deploy on testpypi (optionnal, site here : https://test.pypi.org/):
# twine upload --repository testpypi dist/*
# 3- upload to PyPi
# twine upload dist/*
# """

# from madoc import __version__
# import pathlib
# from setuptools import setup

# # The directory containing this file
# HERE = pathlib.Path(__file__).parent

# # The text of the README file
# README = (HERE / "README.md").read_text()

# # This call to setup() does all the work
# setup(
#     Name="madoc",
#     # version=f"{__version__}",
#     version="2.0.0",
#     description=(
#         "Documentation generator from markdown files"
#         ),
#     long_description=README,
#     long_description_content_type="text/markdown",
#     url="https://github.com/byoso/madoc",
#     author="Vincent Fabre",
#     author_email="peigne.plume@gmail.com",
#     license="MIT",
#     classifiers=[
#         "License :: OSI Approved :: MIT License",
#         "Programming Language :: Python :: 3",
#         "Development Status :: 5 - Production/Stable",
#         "License :: OSI Approved :: MIT License",
#         "Natural Language :: English",
#     ],
#     packages=[
#         "madoc",
#         "madoc.templates",
#         "madoc.templates.madoc",
#         "madoc.assets",
#         "madoc.silly_engine",
#         ],
#     # include_package_data=True,
#     package_data={'': ['*.tpl', '*.html', '*.ico', '*.css']},
#     python_requires='>=3.8',
#     install_requires=[
#         'Jinja2>=3.1.2,<4.0.0',
#         'markdown>=3.7,<4.0.0',
#         'Pygments>=2.19.1,<3.0.0',
#         'requests>=2.32.3,<3.0.0'
#     ],
#     keywords='markdown html documentation',
#     entry_points={
#         "console_scripts": [
#             "madoc=madoc.main:cmd",
#         ]
#     },
#     setup_requires=['wheel'],
# )
