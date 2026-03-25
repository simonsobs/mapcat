import argparse as ap
import os
from pathlib import Path

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mapcat.database import DepthOneMapTable
from mapcat.toolkit import act, update_sky_coverage

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
        (14, 3),
        (14, 4),
        (14, 6),
        (14, 7),
        (15, 3),
        (15, 4),
        (15, 5),
        (15, 6),
        (15, 7),
        (16, 3),
        (16, 4),
        (16, 5),
        (16, 6),
        (16, 7),
        (17, 3),
        (17, 4),
        (17, 5),
        (17, 6),
        (17, 7),
        (18, 3),
        (18, 4),
        (18, 5),
        (18, 6),
        (18, 7),
        (19, 3),
        (19, 4),
        (19, 5),
        (19, 6),
        (19, 7),
        (20, 3),
        (20, 4),
        (20, 5),
        (20, 6),
        (20, 7),
        (21, 3),
        (21, 4),
        (21, 5),
        (21, 6),
        (21, 7),
        (22, 3),
        (22, 4),
        (22, 5),
        (22, 6),
        (22, 7),
        (23, 3),
        (23, 4),
        (23, 5),
        (23, 6),
        (23, 7),
        (24, 3),
        (24, 4),
        (24, 5),
        (24, 6),
        (24, 7),
        (25, 3),
        (25, 4),
        (25, 5),
        (25, 6),
        (25, 7),
        (26, 3),
        (26, 4),
        (26, 5),
        (26, 6),
        (26, 7),
        (27, 3),
        (27, 4),
        (27, 5),
        (27, 6),
        (27, 7),
        (28, 3),
        (28, 4),
        (28, 5),
        (28, 6),
        (28, 7),
        (29, 3),
        (29, 4),
        (29, 5),
        (29, 6),
    ],
    "1505646390": [(22, 3), (22, 4), (22, 5), (23, 3), (23, 4), (23, 5)],
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
