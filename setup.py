#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'Click>=3.0,<4.0',
]

test_requirements = [
    'pytest',
]

setup(
    name='click-utils',
    version='0.2.2.dev0',
    description='a set of utilites for writing command line programs with Click',
    long_description=readme + '\n\n' + history,
    author=u'Sławek Ehlert',
    author_email='slafs.e@gmail.com',
    url='https://github.com/slafs/click-utils',
    packages=[
        'click_utils',
    ],
    package_dir={'click_utils':
                 'click_utils'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='click-utils',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
