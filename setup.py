#!/usr/bin/env python

from setuptools import setup

setup(
    name='goprocontroller',
    version='0.0.0',
    description='An http API to control multiple GoPro cameras over wifi.',
    long_description='',
    url='https://github.com/joshvillbrandt/goprocontroller',
    author='Josh Villbrandt',
    author_email='josh@javconcepts.com',
    license=open('LICENSE').read(),
    packages=[],
    setup_requires=[],
    install_requires=[
        'goprohero==0.2.6',
        'wireless==0.3.0',
        'django==1.7.1',
        'djangorestframework',
        'django-cors-headers',
        'python-dateutil',
        'colorama'
    ],
    scripts=[
        'scripts/goprospammer',
        'scripts/goprologger'
    ],
    test_suite='tests',
    zip_safe=False
)
