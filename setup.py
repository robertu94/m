#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name="m",
     version="2.2.0",
     description="a software build tool",
     long_description="file: README.md",
     author="Robert Underwood",
     author_email="rr.underwood94@gmail.com",
     url="https://github.com/robertu94/m",
     packages=find_packages(),
     entry_points= {
         'console_scripts': [ 'm = m.__main__:main']
     }
)
