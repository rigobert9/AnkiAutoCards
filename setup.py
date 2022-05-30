#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "ankiautocards",
    version = "1.0.0",
    packages = find_packages(),
    #include_package_data = True,
    install_requires=["anki", "argparse", "aqt", "re"])
