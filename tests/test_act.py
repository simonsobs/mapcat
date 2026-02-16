import argparse as ap
import os
from pathlib import Path

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import mapcat.toolkit.act as act
import mapcat.toolkit.update_sky_coverage as update_sky_coverage
from mapcat.database import DepthOneMapTable

DATA_URLS = [
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505603190_pa4_f150_info.hdf",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505603190_pa4_f150_ivar.fits",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505603190_pa4_f150_kappa.fits",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505603190_pa4_f150_map.fits",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505603190_pa4_f150_rho.fits",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505603190_pa4_f150_time.fits",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505646390_pa6_f150_info.hdf",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505646390_pa6_f150_ivar.fits",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505646390_pa6_f150_kappa.fits",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505646390_pa6_f150_map.fits",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505646390_pa6_f150_rho.fits",
    "https://g-0a470a.6b7bd8.0ec8.data.globus.org/act_dr6/dr6.02/depth1/depth1_maps/15056/depth1_1505646390_pa6_f150_time.fits",
]

cov_mapping = {
    "1505603190": [
        (-4, 3),
        (-4, 4),
        (-4, 6),
        (-4, 7),
        (-3, 3),
        (-3, 4),
        (-3, 5),
        (-3, 6),
        (-3, 7),
        (-2, 3),
        (-2, 4),
        (-2, 5),
        (-2, 6),
        (-2, 7),
        (-1, 3),
        (-1, 4),
        (-1, 5),
        (-1, 6),
        (-1, 7),
        (0, 3),
        (0, 4),
        (0, 5),
        (0, 6),
        (0, 7),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 7),
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 6),
        (2, 7),
        (3, 3),
        (3, 4),
        (3, 5),
        (3, 6),
        (3, 7),
        (4, 3),
        (4, 4),
        (4, 5),
        (4, 6),
        (4, 7),
        (5, 3),
        (5, 4),
        (5, 5),
        (5, 6),
        (5, 7),
        (6, 3),
        (6, 4),
        (6, 5),
        (6, 6),
        (6, 7),
        (7, 3),
        (7, 4),
        (7, 5),
        (7, 6),
        (7, 7),
        (8, 3),
        (8, 4),
        (8, 5),
        (8, 6),
        (8, 7),
        (9, 3),
        (9, 4),
        (9, 5),
        (9, 6),
        (9, 7),
        (10, 3),
        (10, 4),
        (10, 5),
        (10, 6),
        (10, 7),
        (11, 3),
        (11, 4),
        (11, 5),
        (11, 6),
    ],
    "1505646390": [(4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)],
}


def run_migration(database_path: str):
    """
    Run the migration on the database.
    """
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(
        __file__.replace("tests/test_act.py", "") + "mapcat/alembic.ini"
    )
    database_url = f"sqlite:///{database_path}"
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")

    return


@pytest.fixture(scope="session", autouse=True)
def database_sessionmaker(tmp_path_factory):
    """
    Create a temporary SQLite database for testing.
    """

    tmp_path = tmp_path_factory.mktemp("mapcat")
    # Create a temporary SQLite database for testing.
    database_path = tmp_path / "test.db"

    # Run the migration on the database. This is blocking.
    run_migration(database_path)

    database_url = f"sqlite:///{database_path}"

    engine = create_engine(database_url, echo=True, future=True)

    yield sessionmaker(bind=engine, expire_on_commit=False)

    # Clean up the database (don't do this in case we want to inspect)
    database_path.unlink()


@pytest.fixture(scope="session")
def downloaded_data_file(request):
    """
    Fixture to download depth 1 maps for testing.

    Parameters
    ----------
    tmp_path_factory : pytest.TempPathFactory
        Factory to create temporary directory for downloaded files
    Returns
    -------
    file_path : str
        Path to the downloaded file
    """

    for url in DATA_URLS:
        cache_dir = Path("../.pytest_cache/d1maps")
        filename = os.path.basename(url)
        subdir = os.path.basename(os.path.dirname(url))
        file_path = cache_dir / subdir / filename

        # Check to see if each file is already downloaded in the cache, if so skip downloading it again
        cached_file = request.config.cache.get(
            "downloaded_file_" + os.path.basename(url), None
        )
        if cached_file and os.path.exists(cached_file):
            continue

        # Download the file
        response = requests.get(url)
        response.raise_for_status()

        # To match the expected directory strcutre, e.g. 15060/ contains depth 1 maps
        # starting at 15060, make the intermediate directory
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(response.content)

        # Set the location of the file in the cache
        request.config.cache.set(
            "downloaded_file_" + os.path.basename(url), str(file_path)
        )

    return cache_dir


def test_act(database_sessionmaker, downloaded_data_file):
    args = ap.Namespace(
        glob="*/*_map.fits",
        relative_to=downloaded_data_file,
        telescope="act",
    )

    act.core(session=database_sessionmaker, args=args)

    with database_sessionmaker() as session:
        maps = session.query(DepthOneMapTable).all()
        assert len(maps) == 2

        # Not the prettiest tests of all time, but whatever.
        for map in maps:
            assert map.tube_slot in ["pa4", "pa6"]
            assert map.frequency == "f150"
            assert map.ctime in [1505603190, 1505646390]


def test_sky_coverage(database_sessionmaker):
    update_sky_coverage.core(session=database_sessionmaker)
    with database_sessionmaker() as session:
        d1maps = session.query(DepthOneMapTable).all()
        print("LEN", len(d1maps))
        for d1map in d1maps:
            print("\n\n\n\nD1MAP: ", d1map.depth_one_sky_coverage)
            assert len(d1map.depth_one_sky_coverage) > 0
            for cov in d1map.depth_one_sky_coverage:
                # Shitty test to make sure the coverage tiles are correct, by checking against the known coverage for these two maps.
                # The coverage tiles are stored in cov_mapping, which is a dict mapping from ctime to a list of (x,y) tuples representing the coverage tiles.
                assert tuple(cov.x, cov.y) in cov_mapping[str(d1map.ctime)]
