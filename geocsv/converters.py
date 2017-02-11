

from decimal import Decimal
from datetime import datetime


def convert_value(coltype, value):
    """Convert a value given a column type."""

    try:
        return CONVERTERS[coltype](value)

    except KeyError:
        raise TypeError('Invalid column type: {}'.format(coltype))


def _parse_datetime(val, fmt='%Y-%m-%d %I:%M:%S%z'):
    """Convert a string time to a datetime.datetime object."""

    try:
        return datetime.strptime(val, fmt)
    except ValueError:
        pass

    # maybe the timezone offset is truncated like -05
    if '%z' in fmt and val[-3] in ('-', '+'):

        val += '00'
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            pass

    # assume there is no timezone
    if fmt.endswith('%z'):
        new_fmt = fmt.rstrip('%z')
        return datetime.strptime(val, new_fmt)

    raise ValueError('Datetime {} does not match format {}'.format(val, fmt))


def convert_to_time(val):
    """Convert a string time to a datetime.time object."""

    try:
        return _parse_datetime(val, '%I:%M:%S%z').time()
    except ValueError:
        raise ValueError('Invalid value for Time column: {}'.format(val))


def convert_to_datetime(val):
    """Convert a string time to a datetime.datetime object."""

    # assume time with proper timezone offset like -0500
    try:
        return _parse_datetime(val, '%Y-%m-%d %I:%M:%S%z')
    except ValueError:
        pass

    # assume there is no time component
    try:
        return datetime.strptime(val, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Invalid value for DateTime column: {}'.format(val))


CONVERTERS = {
    'WKT': str,
    'Integer64': int,
    'Integer': int,
    'Real': Decimal,
    'String': str,
    'Date': lambda x: datetime.strptime(x, '%Y-%m-%d').date(),
    'Time': convert_to_time,
    'DateTime': convert_to_datetime,
    'Binary': lambda x: x
}
