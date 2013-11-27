#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages


READMEFILE = "README.rst"
VERSIONFILE = os.path.join("douglas", "__init__.py")
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"


def get_version():
    verstrline = open(VERSIONFILE, "rt").read()
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError(
            "Unable to find version string in %s." % VERSIONFILE)


setup(
    name="douglas",
    version=get_version(),
    description="Douglas is a file-based blog system.",
    long_description=open(READMEFILE).read(),
    license='MIT',
    author="Will Kahn-Greene",
    author_email="willkg@bluesock.org",
    keywords="blog",
    url="https://github.com/willkg/douglas/",
    requires=['Jinja2'],
    packages=find_packages(),
    scripts=["bin/douglas-cmd"],
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
    ]
)
