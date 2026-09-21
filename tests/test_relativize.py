"""
Tests for the mapcatrelativize CLI (mapcat/toolkit/relativize.py).
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mapcat.database import AtomicMapTable, DepthOneCoaddTable, DepthOneMapTable
from mapcat.helper import settings
from mapcat.toolkit.relativize import core, relativize_path


def run_migration(database_path: str):
    """Run the migration on the database."""
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(str(Path(__file__).parent.parent / "mapcat" / "alembic.ini"))
    database_url = f"sqlite:///{database_path}"
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="module", autouse=True)
def database_sessionmaker(tmp_path_factory):
    """Create a temporary SQLite database for testing."""
    tmp_path = tmp_path_factory.mktemp("mapcat_relativize")
    database_path = tmp_path / "test_relativize.db"

    run_migration(database_path)

    database_url = f"sqlite:///{database_path}"
    engine = create_engine(database_url, echo=False, future=True)

    yield sessionmaker(bind=engine, expire_on_commit=False)

    database_path.unlink()


@pytest.fixture
def parents(tmp_path, monkeypatch):
    """Point settings' parent directories at a fresh tmp_path for this test."""
    depth_one_parent = tmp_path / "depth_one"
    depth_one_coadd_parent = tmp_path / "depth_one_coadd"
    atomic_parent = tmp_path / "atomic"

    monkeypatch.setattr(settings, "depth_one_parent", depth_one_parent)
    monkeypatch.setattr(settings, "depth_one_coadd_parent", depth_one_coadd_parent)
    monkeypatch.setattr(settings, "atomic_parent", atomic_parent)

    return {
        "depth_one_map": depth_one_parent,
        "depth_one_coadd": depth_one_coadd_parent,
        "atomic_map": atomic_parent,
    }


def _make_map(session, name, ctime, map_path):
    with session() as s:
        dmap = DepthOneMapTable(
            map_name=name,
            map_path=map_path,
            tube_slot="OTi1",
            frequency="f090",
            ctime=datetime.fromtimestamp(ctime, tz=timezone.utc),
            start_time=datetime.fromtimestamp(ctime - 500, tz=timezone.utc),
            stop_time=datetime.fromtimestamp(ctime + 500, tz=timezone.utc),
        )
        s.add(dmap)
        s.commit()
        s.refresh(dmap)
        return dmap.map_id


def _get_map(session, map_id):
    with session() as s:
        return s.get(DepthOneMapTable, map_id)


def _make_coadd(session, name, ctime, map_path):
    with session() as s:
        coadd = DepthOneCoaddTable(
            coadd_name=name,
            coadd_type="depth1_streaming_coadd",
            map_path=map_path,
            ivar_path=None,
            frequency="f090",
            ctime=datetime.fromtimestamp(ctime, tz=timezone.utc),
            start_time=datetime.fromtimestamp(ctime - 500, tz=timezone.utc),
            stop_time=datetime.fromtimestamp(ctime + 500, tz=timezone.utc),
        )
        s.add(coadd)
        s.commit()
        s.refresh(coadd)
        return coadd.coadd_id


def _get_coadd(session, coadd_id):
    with session() as s:
        return s.get(DepthOneCoaddTable, coadd_id)


def _make_atomic(session, obs_id, ctime, map_path):
    with session() as s:
        amap = AtomicMapTable(
            obs_id=obs_id,
            telescope="lat",
            freq_channel="f090",
            wafer="w1",
            split_label="full",
            ctime=datetime.fromtimestamp(ctime, tz=timezone.utc),
            map_path=map_path,
        )
        s.add(amap)
        s.commit()
        s.refresh(amap)
        return amap.atomic_map_id


def _get_atomic(session, atomic_map_id):
    with session() as s:
        return s.get(AtomicMapTable, atomic_map_id)


def test_relativize_path_already_relative(tmp_path):
    assert relativize_path("foo/bar.fits", tmp_path, force=False) is None


def test_relativize_path_under_parent(tmp_path):
    abs_path = str(tmp_path / "foo" / "bar.fits")
    assert relativize_path(abs_path, tmp_path, force=False) == "foo/bar.fits"


def test_relativize_path_outside_parent_no_force(tmp_path):
    other = tmp_path / "sibling"
    outside_path = str(other / "bar.fits")
    assert relativize_path(outside_path, tmp_path / "parent", force=False) is None


def test_relativize_path_outside_parent_with_force(tmp_path):
    other = tmp_path / "sibling"
    outside_path = str(other / "bar.fits")
    result = relativize_path(outside_path, tmp_path / "parent", force=True)
    assert result == "../sibling/bar.fits"


def test_core_relativizes_depth_one_map(database_sessionmaker, parents):
    depth_one_parent = parents["depth_one_map"]
    abs_map_path = str(depth_one_parent / "15722" / "map.fits")

    map_id = _make_map(
        database_sessionmaker, "relativize_map", 1755000000.0, abs_map_path
    )

    args = argparse.Namespace(table=["depth_one_map"], dry_run=False, force=False, parent_path=None)
    core(session=database_sessionmaker, args=args)

    dmap = _get_map(database_sessionmaker, map_id)
    assert dmap.map_path == "15722/map.fits"


def test_core_dry_run_does_not_write(database_sessionmaker, parents):
    depth_one_parent = parents["depth_one_map"]
    abs_map_path = str(depth_one_parent / "dryrun" / "map.fits")

    map_id = _make_map(
        database_sessionmaker, "relativize_dryrun", 1755100000.0, abs_map_path
    )

    args = argparse.Namespace(table=["depth_one_map"], dry_run=True, force=False, parent_path=None)
    core(session=database_sessionmaker, args=args)

    dmap = _get_map(database_sessionmaker, map_id)
    assert dmap.map_path == abs_map_path


def test_core_already_relative_untouched(database_sessionmaker, parents):
    map_id = _make_map(
        database_sessionmaker,
        "relativize_already_rel",
        1755200000.0,
        "already/relative.fits",
    )

    args = argparse.Namespace(table=["depth_one_map"], dry_run=False, force=False, parent_path=None)
    core(session=database_sessionmaker, args=args)

    dmap = _get_map(database_sessionmaker, map_id)
    assert dmap.map_path == "already/relative.fits"


def test_core_skips_path_outside_parent_without_force(database_sessionmaker, parents):
    outside_path = "/completely/unrelated/map.fits"
    map_id = _make_map(
        database_sessionmaker, "relativize_outside", 1755300000.0, outside_path
    )

    args = argparse.Namespace(table=["depth_one_map"], dry_run=False, force=False, parent_path=None)
    core(session=database_sessionmaker, args=args)

    dmap = _get_map(database_sessionmaker, map_id)
    assert dmap.map_path == outside_path


def test_core_parent_path_overrides_settings(database_sessionmaker, parents, tmp_path):
    """Paths recorded on another machine, unrelated to any configured
    MAPCAT_*_PARENT, are still relativized when --parent-path is given."""
    foreign_root = tmp_path / "global" / "cfs" / "cdirs" / "sobs"
    abs_map_path = str(foreign_root / "17569" / "map.fits")

    map_id = _make_map(
        database_sessionmaker, "relativize_parent_override", 1755350000.0, abs_map_path
    )

    args = argparse.Namespace(
        table=["depth_one_map"],
        dry_run=False,
        force=False,
        parent_path=foreign_root,
    )
    core(session=database_sessionmaker, args=args)

    dmap = _get_map(database_sessionmaker, map_id)
    assert dmap.map_path == "17569/map.fits"


def test_core_relativizes_depth_one_coadd(database_sessionmaker, parents):
    depth_one_coadd_parent = parents["depth_one_coadd"]
    abs_map_path = str(depth_one_coadd_parent / "coadd" / "map.fits")

    coadd_id = _make_coadd(
        database_sessionmaker, "relativize_coadd", 1755400000.0, abs_map_path
    )

    args = argparse.Namespace(table=["depth_one_coadd"], dry_run=False, force=False, parent_path=None)
    core(session=database_sessionmaker, args=args)

    coadd = _get_coadd(database_sessionmaker, coadd_id)
    assert coadd.map_path == "coadd/map.fits"


def test_core_relativizes_atomic_map(database_sessionmaker, parents):
    atomic_parent = parents["atomic_map"]
    abs_map_path = str(atomic_parent / "atomic" / "map.fits")

    atomic_map_id = _make_atomic(
        database_sessionmaker, "obs_relativize", 1755500000.0, abs_map_path
    )

    args = argparse.Namespace(table=["atomic_map"], dry_run=False, force=False, parent_path=None)
    core(session=database_sessionmaker, args=args)

    amap = _get_atomic(database_sessionmaker, atomic_map_id)
    assert amap.map_path == "atomic/map.fits"


def test_core_table_filter_leaves_other_tables_untouched(
    database_sessionmaker, parents
):
    depth_one_parent = parents["depth_one_map"]
    depth_one_coadd_parent = parents["depth_one_coadd"]

    map_id = _make_map(
        database_sessionmaker,
        "relativize_filter_map",
        1755600000.0,
        str(depth_one_parent / "filter" / "map.fits"),
    )
    coadd_id = _make_coadd(
        database_sessionmaker,
        "relativize_filter_coadd",
        1755600500.0,
        str(depth_one_coadd_parent / "filter" / "map.fits"),
    )

    args = argparse.Namespace(table=["depth_one_map"], dry_run=False, force=False, parent_path=None)
    core(session=database_sessionmaker, args=args)

    dmap = _get_map(database_sessionmaker, map_id)
    coadd = _get_coadd(database_sessionmaker, coadd_id)

    assert dmap.map_path == "filter/map.fits"
    # coadd table wasn't in scope, should be untouched (still absolute)
    assert coadd.map_path == str(depth_one_coadd_parent / "filter" / "map.fits")
