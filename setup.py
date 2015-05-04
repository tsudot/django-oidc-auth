# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='django-oidc-auth',
    version='0.0.9',
    description='OpenID Connect client for Django applications',
    long_description='WIP',
    author='Lucas S. Magalhães',
    author_email='lucas.sampaio@intelie.com.br',
    packages=find_packages(exclude=['*.tests']),
    include_package_data=True,
    install_requires=[
        'Django',
        'South',
        'pyjwkest==0.6.1',
        'requests',
    ],
    zip_safe=True
)
