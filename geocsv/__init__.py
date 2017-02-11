
import csv
import sys
import itertools
from collections import OrderedDict

from .coltypes import parse_coltype
from .converters import convert_value


def get_header_row(fpath, delim=',', lowercase=False):
    """Read first row of a CSV file."""

    with open(fpath, 'r') as fh:

        rdr = csv.reader(fh, delimiter=delim)
        hdr = [i.strip() for i in next(rdr)]

    if lowercase:
        hdr = [i.lower() for i in hdr]

    return hdr


def get_schema(fpath, csvt_path, delim=';'):
    """Get information on column names and types."""

    colnames = get_header_row(fpath, delim=delim, lowercase=True)
    return OrderedDict(zip(colnames, read_csvt(csvt_path)))


def build_mysql_schema(fpath, csvt_path, tblname, delim=';'):
    """Make create table and insert statements suitable for MySQL."""

    schema = get_schema(fpath, csvt_path, delim)

    create = """
        CREATE TABLE IF NOT EXISTS {} (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,""".format(tblname)

    placeholders = []

    for colname, info in schema.items():
        create += """
            {} {} DEFAULT NULL,""".format(colname, info[2])

        value = 'ST_GeomFromText(%({})s)' if info[0] == 'WKT' else '%({})s'
        placeholders.append(value.format(colname))

    create += """
            PRIMARY KEY (id)
        );"""

    # insert statement
    insert = "INSERT INTO {} ({}) VALUES ({});".format(
        tblname,
        ', '.join(schema.keys()),
        ', '.join(placeholders)
    )

    return create, insert


def read_csvt(csvt_path):
    """Read a GeoCSV schema from .csvt file."""

    hdr = get_header_row(csvt_path, delim=',', lowercase=False)
    return [parse_coltype(i) for i in hdr]


def read_geocsv(fpath, csvt_path=None, delim=';'):
    """Read a GeoCSV file and schema."""

    curlim = csv.field_size_limit(sys.maxsize)

    with open(fpath, 'r') as fh:

        rdr = csv.reader(fh, delimiter=delim)
        hdr = [i.strip().lower() for i in next(rdr)]

        # get types from csvt file
        if csvt_path is not None:
            coltypes = OrderedDict(zip(hdr, read_csvt(csvt_path)))
        else:
            coltypes = OrderedDict(
                zip(hdr, itertools.cycle([('String', None, 'VARCHAR(255)')]))
            )

        yield from (
            {k: convert_value(coltypes[k][0], v) for k, v in zip(hdr, record)}
            for record in rdr
        )

    csv.field_size_limit(curlim)
