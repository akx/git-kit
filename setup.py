# -*- coding: utf-8 -*-
from setuptools import setup

from gitkit import __version__

setup(
    name="git-kit",
    version=__version__,
    entry_points={"console_scripts": ["git-kit=gitkit:cli"]},
    description="A toolkit for Git",
    author="Aarni Koskela",
    author_email="akx@iki.fi",
    license="MIT",
    install_requires=[
        "click==6.3",
        "six==1.10.0"
    ],
    packages=["gitkit"],
)
