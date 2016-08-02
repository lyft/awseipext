import os

from setuptools import setup, find_packages

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

about = {}
with open(os.path.join(ROOT, "awseipext", "__about__.py")) as f:
    exec (f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__email__"],
    url=about["__uri__"],
    description=about["__summary__"],
    license=about["__license__"],
    packages=find_packages(exclude=["test*"]),
    install_requires=[
        'kmsauth>=0.1.5,<0.2.0',
        'marshmallow>=2.9.0,<3.0.0'
    ],
    extras_require={
        'tests': [
            'coverage==4.1',
            'flake8==2.6.2',
            'mccabe==0.5.0',
            'mock==1.0.1',
            'pep8==1.7.0',
            'py==1.4.31',
            'pyflakes==1.2.3',
            'pytest==2.9.2'
        ]
    },
    entry_points={
        "console_scripts": [
            "awseipext = awseipext.client:main"
        ]
    }
)
