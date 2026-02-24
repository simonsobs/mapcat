"""
Tests for the mapcatreset CLI (mapcat/toolkit/reset.py).
"""

import argparse

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mapcat.database import DepthOneMapTable, TimeDomainProcessingTable
from mapcat.toolkit.reset import VALID_STATUSES, core


def run_migration(database_path: str):
    """Run the migration on the database."""
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(
        str(Path(__file__).parent.parent / "mapcat" / "alembic.ini")
    )
    database_url = f"sqlite:///{database_path}"
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="module", autouse=True)
def database_sessionmaker(tmp_path_factory):
    """Create a temporary SQLite database for testing."""
    tmp_path = tmp_path_factory.mktemp("mapcat_reset")
    database_path = tmp_path / "test_reset.db"

    run_migration(database_path)

    database_url = f"sqlite:///{database_path}"
    engine = create_engine(database_url, echo=False, future=True)

    yield sessionmaker(bind=engine, expire_on_commit=False)

    database_path.unlink()


def _make_map(session, name, ctime, start_time=None, stop_time=None):
    """Helper to insert a DepthOneMapTable row and return its map_id."""
    with session() as s:
        dmap = DepthOneMapTable(
            map_name=name,
            map_path=f"/path/{name}_map.fits",
            tube_slot="OTi1",
            frequency="f090",
            ctime=ctime,
            start_time=start_time or ctime - 500,
            stop_time=stop_time or ctime + 500,
        )
        s.add(dmap)
        s.commit()
        s.refresh(dmap)
        return dmap.map_id


def _make_proc(session, map_id, status):
    """Helper to insert a TimeDomainProcessingTable row and return its id."""
    with session() as s:
        proc = TimeDomainProcessingTable(
            map_id=map_id,
            processing_start=1756000000.0,
            processing_end=1756001000.0,
            processing_status=status,
        )
        s.add(proc)
        s.commit()
        s.refresh(proc)
        return proc.processing_status_id


def _get_proc(session, proc_id):
    """Return a TimeDomainProcessingTable row or None."""
    with session() as s:
        return s.get(TimeDomainProcessingTable, proc_id)


def test_valid_statuses():
    assert "failed" in VALID_STATUSES
    assert "completed" in VALID_STATUSES
    assert "permafail" in VALID_STATUSES


def test_reset_all_to_failed(database_sessionmaker):
    """Reset all processing statuses to 'failed'."""
    map_id = _make_map(database_sessionmaker, "reset_all_map", 1755000000.0)
    proc_id = _make_proc(database_sessionmaker, map_id, "running")

    args = argparse.Namespace(
        status="failed",
        map_id=None,
        start_time=None,
        end_time=None,
        from_status=None,
    )
    core(session=database_sessionmaker, args=args)

    proc = _get_proc(database_sessionmaker, proc_id)
    assert proc is not None
    assert proc.processing_status == "failed"


def test_reset_by_map_id(database_sessionmaker):
    """Reset only the entry for a specific map ID."""
    map_id_a = _make_map(database_sessionmaker, "reset_mapid_a", 1755100000.0)
    map_id_b = _make_map(database_sessionmaker, "reset_mapid_b", 1755200000.0)

    proc_id_a = _make_proc(database_sessionmaker, map_id_a, "running")
    proc_id_b = _make_proc(database_sessionmaker, map_id_b, "running")

    args = argparse.Namespace(
        status="completed",
        map_id=[map_id_a],
        start_time=None,
        end_time=None,
        from_status=None,
    )
    core(session=database_sessionmaker, args=args)

    proc_a = _get_proc(database_sessionmaker, proc_id_a)
    proc_b = _get_proc(database_sessionmaker, proc_id_b)

    assert proc_a.processing_status == "completed"
    # proc_b should be unchanged (still "running")
    assert proc_b.processing_status == "running"


def test_reset_by_time_range(database_sessionmaker):
    """Reset only entries whose map ctime falls within a time range."""
    map_id_early = _make_map(database_sessionmaker, "reset_time_early", 1754000000.0)
    map_id_late = _make_map(database_sessionmaker, "reset_time_late", 1756000000.0)

    proc_id_early = _make_proc(database_sessionmaker, map_id_early, "running")
    proc_id_late = _make_proc(database_sessionmaker, map_id_late, "running")

    args = argparse.Namespace(
        status="failed",
        map_id=None,
        start_time=1753000000.0,
        end_time=1755000000.0,
        from_status=None,
    )
    core(session=database_sessionmaker, args=args)

    proc_early = _get_proc(database_sessionmaker, proc_id_early)
    proc_late = _get_proc(database_sessionmaker, proc_id_late)

    assert proc_early.processing_status == "failed"
    # proc_late's ctime is outside the range, should be unchanged
    assert proc_late.processing_status == "running"


def test_reset_by_from_status(database_sessionmaker):
    """Only reset entries that currently have a specific status."""
    map_id_a = _make_map(database_sessionmaker, "reset_from_a", 1755300000.0)
    map_id_b = _make_map(database_sessionmaker, "reset_from_b", 1755400000.0)

    proc_id_a = _make_proc(database_sessionmaker, map_id_a, "running")
    proc_id_b = _make_proc(database_sessionmaker, map_id_b, "failed")

    args = argparse.Namespace(
        status="completed",
        map_id=None,
        start_time=None,
        end_time=None,
        from_status="running",
    )
    core(session=database_sessionmaker, args=args)

    proc_a = _get_proc(database_sessionmaker, proc_id_a)
    proc_b = _get_proc(database_sessionmaker, proc_id_b)

    assert proc_a.processing_status == "completed"
    # proc_b was "failed", not "running", so it should be untouched
    assert proc_b.processing_status == "failed"


def test_remove_entries_no_status(database_sessionmaker):
    """When no status is given, entries should be deleted (reset to none)."""
    map_id = _make_map(database_sessionmaker, "reset_remove_map", 1755500000.0)
    proc_id = _make_proc(database_sessionmaker, map_id, "running")

    args = argparse.Namespace(
        status=None,
        map_id=[map_id],
        start_time=None,
        end_time=None,
        from_status=None,
    )
    core(session=database_sessionmaker, args=args)

    proc = _get_proc(database_sessionmaker, proc_id)
    assert proc is None


def test_permafail_status(database_sessionmaker):
    """Set a processing entry to 'permafail'."""
    map_id = _make_map(database_sessionmaker, "reset_permafail_map", 1755600000.0)
    proc_id = _make_proc(database_sessionmaker, map_id, "running")

    args = argparse.Namespace(
        status="permafail",
        map_id=[map_id],
        start_time=None,
        end_time=None,
        from_status=None,
    )
    core(session=database_sessionmaker, args=args)

    proc = _get_proc(database_sessionmaker, proc_id)
    assert proc is not None
    assert proc.processing_status == "permafail"


def test_combined_filters(database_sessionmaker):
    """Combine map_id and from_status filters."""
    map_id_a = _make_map(database_sessionmaker, "reset_combo_a", 1755700000.0)
    map_id_b = _make_map(database_sessionmaker, "reset_combo_b", 1755800000.0)

    proc_id_a = _make_proc(database_sessionmaker, map_id_a, "running")
    proc_id_b = _make_proc(database_sessionmaker, map_id_b, "running")

    # Only reset map_id_a if its status is "running"
    args = argparse.Namespace(
        status="failed",
        map_id=[map_id_a],
        start_time=None,
        end_time=None,
        from_status="running",
    )
    core(session=database_sessionmaker, args=args)

    proc_a = _get_proc(database_sessionmaker, proc_id_a)
    proc_b = _get_proc(database_sessionmaker, proc_id_b)

    assert proc_a.processing_status == "failed"
    assert proc_b.processing_status == "running"
