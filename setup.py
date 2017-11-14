from setuptools import setup, find_packages
import sys, os

version = '3.0.1'

setup(
    name='ckanext-odm_laws',
    version=version,
    description="OD Mekong CKAN's law extension",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Christopher Krempel',
    author_email='info@aeviator.cc',
    url='http://www.aeviaor.cc',
    license='AGPL3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        odm_laws=ckanext.odm_laws.plugin:OdmLawsPlugin
    ''',
)
