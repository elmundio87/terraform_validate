from setuptools import setup, find_packages

setup(
    name="terraform_validate",
    version="1.0",
    packages = find_packages(),
    install_requires=[
        "pyhcl"
    ],
)