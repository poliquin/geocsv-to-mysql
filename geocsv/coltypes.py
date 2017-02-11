
import re

"""
Convert a GeoCSV column type to a suitable MySQL type.
"""


def parse_coltype(txt):
    """Parse a column specification into a type, subtype tuple."""

    m = FIELD.match(txt)
    if m is None:
        raise TypeError('Invalid column type: {}'.format(txt))

    coltype, subtype = m.groups()
    return coltype, subtype, MYSQL_TYPES[coltype](subtype)


def mysql_real_type(subtype=None):
    """Determine real column type."""

    try:
        return {None: 'DOUBLE', 'Float32': 'FLOAT'}[subtype]
    except KeyError:
        pass

    # assume subtype is a precision
    prec = re.match(r'([0-9]+)[.,]([0-9]+)', subtype)
    if prec is None:
        raise ValueError('Invalid subtype for Real column: {}'.format(subtype))

    m, n = int(prec.group(1)), int(prec.group(2))
    return 'DECIMAL({}, {})'.format(m, n)


def _mysql_int_length(subtype):
    """Determine smallest field that can hold data with given length."""

    try:
        length = int(subtype)
    except ValueError:
        raise ValueError(
            'Invalid subtype for Integer column: {}'.format(subtype)
        )

    if length < 3:
        kind = 'TINYINT'
    elif length < 4:
        kind = 'SMALLINT'
    elif length < 7:
        kind = 'MEDIUMINT'
    elif length <= 10:
        kind = 'INT'
    else:
        kind = 'BIGINT'

    return '{}({})'.format(kind, length)


def mysql_integer_type(subtype=None):
    """Determine integer column type."""

    try:
        return {None: 'INT', 'Int16': 'SMALLINT', 'Boolean': 'BOOLEAN'}[subtype]
    except KeyError:
        pass

    return _mysql_int_length(subtype)


def mysql_string_type(subtype=None, varchar_only=False):

    if subtype is None:
        return 'VARCHAR(255)'

    try:
        length = int(subtype)

    except ValueError:
        raise ValueError(
            'Invalid subtype for String column: {}'.format(subtype)
        )

    if not varchar_only and length <= 4:
        return 'CHAR({})'.format(length)
    else:
        return 'VARCHAR({})'.format(length)


FIELD = re.compile(
    r"""(WKT|Integer6?4?|Real|String|Date|Time|DateTime|Binary)
        (?:\(([0-9.]+|Boolean|Int16|Float32)\))?
     """,
    re.I | re.X
)

MYSQL_TYPES = {
    'WKT': lambda x: 'GEOMETRY',
    'Integer64': lambda x: 'BIGINT',
    'Integer': mysql_integer_type,
    'Real': mysql_real_type,
    'String': mysql_string_type,
    'Date': lambda x: 'DATE',
    'Time': lambda x: 'TIME',
    'DateTime': lambda x: 'DATETIME',
    'Binary': lambda x: 'BLOB'
}
