import setuptools
from pathlib import Path

setuptools.setup(
    name="shs_identification",
    version=1.02,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(
        exclude=["draft.ipynb", "draft2.ipyn", "venv"]),
    install_requires=Path("requirements.txt").read_text().split("\n")[:-1]
)
