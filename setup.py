# -*- coding: utf8 -*-

from distutils.core import setup

setup(
    name='geocsv',
    packages=['geocsv'],
    version='0.1.0',
    description='Load GeoCSV into MySQL database',
    author='Chris Poliquin',
    author_email='chrispoliquin@gmail.com',
    url='',
    keywords=['geocsv', 'mysql', 'shapefile', 'geometry', 'ogr2ogr'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        ],
    long_description="""\
Load GeoCSV into MySQL database
-------------------------------

This package makes it easy to load a GeoCSV file into a MySQL table.
It parses the CSVT file to infer column types and builds the table,
then populates with records from the CSV file.

The benefit of this script is it avoids the need for a MySQL driver
for GDAL's ogr2ogr tool. Simply convert to GeoCSV and use this script
to load the geometry into MySQL.
"""
)
