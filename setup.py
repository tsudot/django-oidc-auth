# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='django-oidc-auth',
    version='0.0.5',
    description='OpenID Connect client for Django applications',
    long_description='WIP',
    author='Lucas S. Magalhães',
    author_email='lucas.sampaio@intelie.com.br',
    packages=find_packages(exclude=['*.tests']),
    include_package_data=True,
    install_requires=[
        'Django',
        'South',
        'pyjwkest',
        'requests',
    ],
    zip_safe=True
)
