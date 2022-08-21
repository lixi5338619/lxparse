# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()


setup(
    name="lxparse",
    url="https://github.com/lixi5338619/lxparse",
    version= '1.0.1',
    description="A library for intelligently parsing list page links and details page contents",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="lx",
    author_email="125066648@qq.com",
    keywords="python web crawl HtmlParse",
    maintainer='lx',
    packages = find_packages(),
    platforms=["all"],
    install_requires=[
        'lxml',
        'lxpy',
        ],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)


## python setup.py sdist bdist_wheel
## twine upload dist/*