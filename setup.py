#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine --dev
# Then you can run `python setup.py upload` to upload the distribution.

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Import your package
import pbf

# Package meta-data.
NAME = 'PigBotFramework'
DESCRIPTION = 'PigBotFramework is a fast, easy-to-use, intelligent robot framework.'
URL = 'https://github.com/PigBotFramework/next'
EMAIL = 'admin@xzynb.top'
AUTHOR = 'XzyStudio'
REQUIRES_PYTHON = '>=3.8.0'

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

with io.open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    data = f.read().split('\n')
    REQUIRED = []
    for i in data:
        if i.strip() == '':
            continue
        i = i.split('==')[0]
        REQUIRED.append(i)

VERSION = pbf.version


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git…')
        os.system(f'git add . && git commit -m "Upload version:{VERSION}" && git push origin main')
        os.system('git tag v{0}'.format(VERSION))
        os.system('git push --tags')

        self.status("Build docs...")
        os.system(f'pdoc -o docbuild --footer-text "PBF Next ({VERSION}) Docs" --favicon https://pbf.xzynb.top/statics/images/head.jpg --math --search --logo https://pbf.xzynb.top/statics/images/head.jpg ./pbf')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
