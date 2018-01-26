
import os
import argparse
import mysql.connector

from . import build_mysql_schema
from . import read_geocsv


def make_table_name(fpath):
    """Create a MySQL table name from a filepath."""

    *_, fname = os.path.split(fpath)
    tbl, *_ = os.path.splitext(fname)

    return tbl


def config_ssl(dirpath):
    """Find SSL certificates for MySQL connection."""

    if dirpath is not None and os.path.isdir(dirpath):

        ca = os.path.join(dirpath, 'ca-cert.pem')
        cert = os.path.join(dirpath, 'client-cert.pem')
        key = os.path.join(dirpath, 'client-key.pem')

        return {
            'ssl_ca': ca if os.path.exists(ca) else None,
            'ssl_cert': cert if os.path.exists(cert) else None,
            'ssl_key': key if os.path.exists(key) else None
        }

    else:
        return {}


def main(opts):
    """Parse and load GeoCSV file."""

    if opts.table is None:
        opts.table = make_table_name(opts.fpath)

    if opts.csvt_path is None:
        opts.csvt_path = opts.fpath + 't'

    if not os.path.isfile(opts.fpath):
        raise IOError('No GeoCSV file {}'.format(opts.fpath))

    if not os.path.isfile(opts.csvt_path):
        raise IOError(
            'GeoCSV {} has no schema {}'.format(opts.fpath, opts.csvt_path)
        )

    create, insert = build_mysql_schema(
        opts.fpath, opts.csvt_path, opts.table, opts.delim
    )

    cnx = mysql.connector.connect(
        host=opts.host,
        user=opts.user,
        password=opts.password,
        database=opts.database,
        **config_ssl(opts.ssldir)
    )

    cur = cnx.cursor()
    cur.execute(create)

    for record in read_geocsv(opts.fpath, opts.csvt_path, opts.delim, opts.enc):
        cur.execute(insert, record)

    cnx.commit()
    cur.close()
    cnx.close()


if __name__ == '__main__':

    argp = argparse.ArgumentParser(description='Load GeoCSV into MySQL')
    argp.add_argument('database', help='Name of MySQL database')
    argp.add_argument('fpath', help='Path to GeoCSV file')
    argp.add_argument('csvt_path', nargs='?', help='Path to CSVT schema file')
    argp.add_argument('-d', '--delim', default=';', help='GeoCSV delimiter')
    argp.add_argument('-i', '--host', default='127.0.0.1')
    argp.add_argument('-u', '--user', default='root')
    argp.add_argument('-p', '--password', nargs='?', default=argparse.SUPPRESS)
    argp.add_argument('-t', '--table', help='Table name')
    argp.add_argument('-s', '--ssldir', default='/etc/mysql-ssl', help='Certs')
    argp.add_argument('-e', '--enc', default='utf8', help='CSV file encoding')

    opts = argp.parse_args()

    if not hasattr(opts, 'password'):
        from getpass import getpass
        opts.password = getpass(
            'Enter password for {}@{}: '.format(opts.user, opts.host)
        )

    main(opts)
