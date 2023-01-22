#!/usr/bin/env python

import os

try:
    from setuptools import setup
except ImportError:
    exit("This package requires Python version >= 3.6 and Python's setuptools")

here = os.path.abspath(os.path.dirname(__file__))

#with open(os.path.join(here, 'requirements.txt')) as f:
#    requirements = f.read().splitlines()


with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

with open(os.path.join(here, 'dt_sms_sdk', 'VERSION')) as f:
    lines = f.read().splitlines()
    try:
        version = [line.split('=')[1] for line in lines if line.startswith('DTSMSAPISDK')][0]
    except IndexError:
        exit("Invalid package version in %s" % os.path.join(here, 'dt_sms_sdk', 'VERSION'))

setup(
    name="unofficial-dt-sms-api-sdk",
    version=version,
    description="Unofficial Python-SDK for the SMS API of Deutsche Telekom",
    long_description=long_description,
    url="https://github.com/Anrufliste/dt-sms-api-sdk-python",
    author='Emil Thies',
    author_email='uDTSMSAPISDK@anrufliste.com',
    packages=["dt_sms_sdk"],
    python_requires='>=3.7',
    include_package_data=True
)
