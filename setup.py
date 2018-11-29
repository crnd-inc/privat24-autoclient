#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='privat24-autoclient-sdk-python',
    version='1.0',
    description='Privat24 Python SDK',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests'],
    # py_modules=['privat24-autoclient-sdk.py'],
)
