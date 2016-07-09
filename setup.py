#!/usr/bin/python

import re
import ast

from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('pps.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name="pps",
    version=version,
    py_modules=["pps"],
    author="Huoty",
    author_email="sudohuoty@gmail.com",
    maintainer="Huoty",
    url="https://github.com/kuanghy/pps",
    description="Linux 'ps -aux' command wrapper.",
    license="MIT",
)
