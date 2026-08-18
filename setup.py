"""Setuptools entry point for the pure-Python pysysmlv2 distribution."""

import re
from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).resolve().parent
META = {}
exec((ROOT / "pysysmlv2" / "config" / "meta.py").read_text(encoding="utf-8"), META)


def _requirements(name):
    path = ROOT / name
    if not path.exists():
        return []
    values = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            values.append(line)
    return values


extra_requirements = {}
for path in ROOT.glob("requirements-*.txt"):
    match = re.fullmatch(r"requirements-(\w+)\.txt", path.name)
    if match:
        extra_requirements[match.group(1)] = _requirements(path.name)

package_data = {
    "pysysmlv2.syntax.generated": ["*.g4", "*.py", "*.tokens", "*.interp", "*.json"],
}

setup(
    name=META["__PACKAGE_NAME__"],
    version=META["__VERSION__"],
    description=META["__DESCRIPTION__"],
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author=META["__AUTHOR__"],
    author_email=META["__AUTHOR_EMAIL__"],
    url="https://github.com/HansBug/pysysmlv2",
    packages=find_packages(include=("pysysmlv2", "pysysmlv2.*", "tools")),
    package_data=package_data,
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=_requirements("requirements.txt"),
    extras_require=extra_requirements,
    entry_points={"console_scripts": ["pysysmlv2=pysysmlv2.__main__:main"]},
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Documentation": "https://pysysmlv2.readthedocs.io/",
        "Source": "https://github.com/HansBug/pysysmlv2",
        "Issues": "https://github.com/HansBug/pysysmlv2/issues",
    },
)
