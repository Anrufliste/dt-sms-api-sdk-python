#!/usr/bin/env python

import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()


setuptools.setup(
    name="unofficial-dt-sms-api-sdk",
    description="Unofficial Python-SDK for the SMS API of Deutsche Telekom",
    long_description=long_description,
    url="https://github.com/Anrufliste/dt-sms-api-sdk-python",
    author='Emil Thies',
    author_email='uDTSMSAPISDK@anrufliste.com',
    python_requires='>=3.7',
    packages=setuptools.find_packages(where='dt_sms_sdk'),
    include_package_data=True
)
