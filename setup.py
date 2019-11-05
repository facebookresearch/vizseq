# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from setuptools import setup, find_packages
import sys


if sys.version_info < (3,):
    sys.exit('Sorry, Python 3 is required for vizseq.')

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_content = f.read()

with open('vizseq/VERSION') as f:
    version = f.read()

setup(
    name='vizseq',
    version=version,
    description='Visual Analysis Toolkit for Text Generation Tasks',
    url='https://github.com/facebookresearch/vizseq',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    setup_requires=[
        'setuptools>=18.0',
    ],
    install_requires=[
        'numpy',
        'sacrebleu',
        'torch',
        'tqdm',
        'nltk',
        'py-rouge',
        'langid',
        'google-cloud-translate',
        'jinja2',
        'IPython',
        'matplotlib',
        'tornado',
        'pandas',
        'soundfile',
        'laserembeddings',
        'bert-score',
    ],
    packages=find_packages(exclude=['examples', 'tests']),
    package_data={'vizseq': ['_templates/*.html', 'VERSION']},
    test_suite='tests',
    zip_safe=False,
)
