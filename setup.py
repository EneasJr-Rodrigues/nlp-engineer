#! /usr/bin/env python3
import os

from setuptools import setup, find_namespace_packages

PROJECT_DIR = os.path.dirname(__file__)

INFO = open(os.path.join(PROJECT_DIR, 'INFO')).readlines()
INFO = dict((line.strip().split('=') for line in INFO))

DEPENDENCIES = open(os.path.join(PROJECT_DIR, 'requirements.txt')).readlines()

setup(name='nlp-engineer',
      version=INFO['version'],
      author=INFO['author'],
      author_email=INFO['author_email'],
      url=INFO['url'],
      license=open(os.path.join(PROJECT_DIR, 'LICENSE')).read(),
      python_requires='>=3.8',
      packages=find_namespace_packages(include=['nlp.engineer','nlp.engineer.*']),
      namespace_packages=['nlp', 'nlp.engineer'],
      install_requires=[d for d in DEPENDENCIES if '://' not in d],
      tests_require=['pytest', 'parameterized'],
      zip_safe=False)
