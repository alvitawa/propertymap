
from setuptools import setup, find_packages

setup(
    # Application name:
    name="PropertyMap",

    # Version number (initial):
    version="0.1",

    # Application author details:
    author="Alvitawa",
    author_email="alfonsotabo@gmail.com",

    # Packages
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="",

    #
    # license="LICENSE.txt",
    description="Fast but RAM-consuming data retrieval.",

    long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[],
)