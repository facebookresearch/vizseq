# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from setuptools import setup, find_packages
import sys


if sys.version_info < (3, 8):
    sys.exit('Sorry, Python 3.8+ is required for vizseq.')

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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    setup_requires=[
        'setuptools>=18.0',
    ],
    install_requires=[
        'numpy>=1.20.0,<3.0.0',
        'sacrebleu>=1.4.13,<3.0.0',
        'torch>=1.9.0',
        'tqdm>=4.0.0',
        'nltk>=3.5,<4.0.0',
        'py-rouge>=1.1',
        'langid>=1.1.6',
        'google-cloud-translate>=3.0.0,<4.0.0',
        'jinja2>=2.11.0,<4.0.0',
        'IPython>=7.0.0',
        'matplotlib>=3.3.0',
        'tornado>=6.0,<7.0',
        'pandas>=1.0.0',
        'soundfile>=0.10.0',
        'laserembeddings>=1.0.0',
        'bert-score>=0.3.0',
    ],
    packages=find_packages(exclude=['examples', 'tests']),
    package_data={'vizseq': ['_templates/*.html', 'VERSION']},
    test_suite='tests',
    zip_safe=False,
)
