from setuptools import setup

setup(
    name="terraform_validate",
    version="1.0",
    package_dir={'': 'src'},
    install_requires=[
        "pyhcl"
    ],
)