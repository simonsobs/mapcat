import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mapcat.database import DepthOneMapTable, TODDepthOneTable
from mapcat.toolkit.mapmaking import build_obslists


def run_migration(database_path: str):
    """
    Run the migration on the database.
    """
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(
        __file__.replace("tests/test_mapmaking.py", "") + "mapcat/alembic.ini"
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


def test_build_obslists(database_sessionmaker):
    # Make some Depth-one maps
    # Note the meta-data doesn't necessarily match between
    # Depth-one maps and tods, sue me
    with database_sessionmaker() as session:
        data1 = DepthOneMapTable(
            map_name="myDepthOne",
            map_path="/PATH/TO/DEPTH/ONE",
            tube_slot="OTi1",
            frequency="f090",
            ctime=1755787524.0,
            start_time=1755687524.0,
            stop_time=1755887524.0,
        )

        data2 = DepthOneMapTable(
            map_name="myDepthOne2",
            map_path="/PATH/TO/DEPTH/ONE2",
            tube_slot="OTi4",
            frequency="f090",
            ctime=1755788524.0,
            start_time=1755787524.0,
            stop_time=1755897524.0,
        )

        session.add(data1)
        session.commit()
        session.refresh(data1)

        session.add(data2)
        session.commit()
        session.refresh(data2)

        map_id1 = data1.map_id
        map_id2 = data2.map_id

    # Get depth one map back
    with database_sessionmaker() as session:
        dmap1 = session.get(DepthOneMapTable, map_id1)
        dmap2 = session.get(DepthOneMapTable, map_id2)

    # Make some TODs
    obs_ids = [
        "obs_1753486724_lati6_111",
        "obs_1753586724_lati6_111",
        "obs_1753686724_lati6_111",
        "obs_1753786724_lati6_111",
    ]
    with database_sessionmaker() as session:
        tod1 = TODDepthOneTable(
            obs_id=obs_ids[0],
            pwv=0.7,
            ctime=1755787524.0,
            start_time=1755687524.0,
            stop_time=1755887524.0,
            nsamples=28562,
            telescope="lat",
            telescope_flavor="lat",
            tube_slot="i6",
            tube_flavor="mf",
            frequency="150",
            scan_type="ops",
            subtype="cmb",
            wafer_count=3,
            duration=100000,
            az_center=180.0,
            az_throw=90.0,
            el_center=50.0,
            el_throw=0.0,
            roll_center=0.0,
            roll_throw=0.0,
            wafer_slots_list="ws0,ws1,ws2",
            stream_ids_list="ufm_mv25,ufm_mv26,ufm_mv11",
            maps=[dmap1],
        )
        tod2 = TODDepthOneTable(
            obs_id=obs_ids[1],
            pwv=0.7,
            ctime=1755787524.0,
            start_time=1755687524.0,
            stop_time=1755887524.0,
            nsamples=28562,
            telescope="lat",
            telescope_flavor="lat",
            tube_slot="i6",
            tube_flavor="mf",
            frequency="150",
            scan_type="ops",
            subtype="cmb",
            wafer_count=3,
            duration=100000,
            az_center=180.0,
            az_throw=90.0,
            el_center=50.0,
            el_throw=0.0,
            roll_center=0.0,
            roll_throw=0.0,
            wafer_slots_list="ws0,ws1,ws2",
            stream_ids_list="ufm_mv25,ufm_mv26,ufm_mv11",
            maps=[dmap1, dmap2],
        )
        tod3 = TODDepthOneTable(
            obs_id=obs_ids[2],
            pwv=0.7,
            ctime=1755787524.0,
            start_time=1755687524.0,
            stop_time=1755887524.0,
            nsamples=28562,
            telescope="lat",
            telescope_flavor="lat",
            tube_slot="i6",
            tube_flavor="mf",
            frequency="150",
            scan_type="ops",
            subtype="cmb",
            wafer_count=3,
            duration=100000,
            az_center=180.0,
            az_throw=90.0,
            el_center=50.0,
            el_throw=0.0,
            roll_center=0.0,
            roll_throw=0.0,
            wafer_slots_list="ws0,ws1,ws2",
            stream_ids_list="ufm_mv25,ufm_mv26,ufm_mv11",
            maps=[dmap2],
        )

        tod4 = TODDepthOneTable(
            obs_id=obs_ids[3],
            pwv=0.7,
            ctime=1755787524.0,
            start_time=1755687524.0,
            stop_time=1755887524.0,
            nsamples=28562,
            telescope="lat",
            telescope_flavor="lat",
            tube_slot="i6",
            tube_flavor="mf",
            frequency="150",
            scan_type="ops",
            subtype="cmb",
            wafer_count=3,
            duration=100000,
            az_center=180.0,
            az_throw=90.0,
            el_center=50.0,
            el_throw=0.0,
            roll_center=0.0,
            roll_throw=0.0,
            wafer_slots_list="ws0,ws1,ws2",
            stream_ids_list="ufm_mv25,ufm_mv26,ufm_mv11",
            maps=[],
        )

        session.add_all([tod1, tod2, tod3, tod4])
        session.commit()

    obs_list = build_obslists(obs_ids=obs_ids, session=session)
    assert obs_list[0][obs_ids[0]][0].map_id == map_id1
    assert obs_list[0][obs_ids[1]][0].map_id == map_id1
    assert obs_list[0][obs_ids[1]][1].map_id == map_id2
    assert obs_list[0][obs_ids[2]][0].map_id == map_id2
    assert obs_ids[3] in obs_list[1]
