#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'thriftpy>=0.3.1',
    'requests>=2.11.1',
    'xylose>=1.31.0'
]

tests_require = []

setup(
    name="citedbyapi",
    version="1.11.2",
    description="SciELO CitedBy service SDK for Python",
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    url="http://github.com/scieloorg/citedbyapi",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    dependency_links=[],
    tests_require=tests_require,
    test_suite='tests',
    install_requires=install_requires
)
