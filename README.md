Simons Observatory Map Catalog
==============================

The Depth-1 and Atomic map catalog for the Simons Observatory.
This repository contains the SQLModel (SQLAlchemy + Pydantic)
types, a client interface, and alembic migration tool for the
database.

Configuration
-------------

`mapcat` is set up to use either PostgreSQL (production) and
SQLite (testing). It can be configured using the `pydantic-settings`
interface defined in `mapcat/helper.py`, with environment variables
using the prefix `MAPCAT_`.

- `MAPCAT_DATABASE_NAME=mapcat.db`: If using PostgreSQL, this should be
  your connection string; for SQLite it should be the path to the map
  catalog file.
- `MAPCAT_DATABASE_TYPE=sqlite`: Or `postgrea` if using PostgreSQL.
- `MAPCAT_DEPTH_ONE_PARENT="."`: Parent directory containing the
  Depth-1 maps referred to by the database on this machine.
- `MAPCAT_ATOMIC_PARENT="."`: Parent directory containing the
  Atomic maps referenced by the database on this machine.

Setting up
----------

Mapcat can be installed like any other python package, using your
preferred package manager. We recommend using `uv`:
```
uv pip install git+https://github.com/simonsobs/mapcat
```
PyPI release builds will be made once the system is more stable.

The database can be migrated (or created, if starting fresh) by using
the `mapcatmigrate` command. This runs `alembic upgrade head` with the
version of the database referred to by your currently installed verison
of the map catalog.

Command-line Tools
------------------

We provide a command-line tool for automatically ingesting a directory
of Depth-1 maps stored in the same format as ACT into the database.
Note that the `_info.hdf` files are required, and that these
are not entirely metadata-complete. The command-line script is:
```
actingest --relative-to=/path/to/maps --glob=*/*_map.fits --telescope=act
```
More information on the parameters is available through `actingest -h`.