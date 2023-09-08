# -*- coding: utf-8 -*-
import os
from setuptools import setup

packages = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)
accepted_filetypes = (".html", ".png", ".svg", ".js", ".css")

for dirpath, dirnames, filenames in os.walk("ab_online"):
    # Ignore dirnames that start with '.'
    if "__init__.py" in filenames or any(
        x.endswith(accepted_filetypes) for x in filenames
    ):
        pkg = dirpath.replace(os.path.sep, ".")
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, ".")
        packages.append(pkg)

if "VERSION" in os.environ:
    version = os.environ["VERSION"]
else:
    version = os.environ.get("GIT_DESCRIBE_TAG", "0.0.0")

setup(
    name="ab-online",
    version=version,
    packages=packages,
    include_package_data=True,
    author="Rémy Le Calloch",
    author_email="remy@lecalloch.net",
    license=open("LICENSE.txt").read(),
    install_requires=[],  # dependency management in conda recipe
    url="https://github.com/Pan6ora/activity-browser-online",
    long_description=open("README.md").read(),
    description="Launch reproducible Activity Browser sessions and distribute them using NoVNC",
    entry_points={
        "console_scripts": [
            "ab-online = ab_online:run_ab_online",
        ]
    },
    package_dir={"": "."},
    package_data={
        "ab_online": ["includes/*", 
        "includes/.*", 
        "includes/config/*", 
        "includes/databases/*",
        "includes/config/fluxbox/*"]
    },
)
