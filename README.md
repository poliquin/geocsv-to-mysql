Load GeoCSV into MySQL database
-------------------------------

This package makes it easy to load a [GeoCSV][geocsv] file into a MySQL
table. It parses the CSVT file to infer column types and builds the table,
then populates with records from the CSV file.

This script avoids the need for a MySQL driver for GDAL's ogr2ogr tool.
Simply convert to GeoCSV and use this to load the geometry into MySQL:

```bash
ogr2ogr -f CSV output.csv input.shp \
    -lco GEOMETRY=AS_WKT -lco SEPARATOR=SEMICOLON -lco CREATE_CSVT=YES

python -m geocsv dbname output.csv -i 127.0.0.1 -u user
```

The above code results in a MySQL table called `output` and the script
automatically looks for a schema file called `output.csvt`. The table name
can be changed with the `--table` flag.

Note that it may be necessary to increase the max packet size on the server
to load large files. This can be done by running the following command on
the server before running geocsv:

    SET GLOBAL max_allowed_packet=134217728;

This program is intended to work with Python 3 and requires the MySQL
Connector for Python.


[geocsv]: https://giswiki.hsr.ch/GeoCSV
