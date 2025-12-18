"""
Test the core functions
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mapcat.database import (
    DepthOneMapTable,
    PipelineInformationTable,
    PointingResidualTable,
    SkyCoverageTable,
    TimeDomainProcessingTable,
    TODDepthOneTable,
    AtomicMapTable,
    AtomicMapCoaddTable,
)


def run_migration(database_path: str):
    """
    Run the migration on the database.
    """
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(
        __file__.replace("tests/test_mapcat.py", "") + "mapcat/alembic.ini"
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


def test_database_exists(database_sessionmaker):
    return


def test_create_depth_one(database_sessionmaker):
    # Create a depth one map
    with database_sessionmaker() as session:
        data = DepthOneMapTable(
            map_name="myDepthOne",
            map_path="/PATH/TO/DEPTH/ONE",
            tube_slot="OTi1",
            frequency="f090",
            ctime=1755787524.0,
            start_time=1755687524.0,
            stop_time=1755887524.0,
        )

        session.add(data)
        session.commit()
        session.refresh(data)

        map_id = data.map_id

    # Get depth one map back
    with database_sessionmaker() as session:
        dmap = session.get(DepthOneMapTable, map_id)

    assert dmap.map_id == map_id
    assert dmap.map_name == "myDepthOne"
    assert dmap.map_path == "/PATH/TO/DEPTH/ONE"
    assert dmap.tube_slot == "OTi1"
    assert dmap.frequency == "f090"
    assert dmap.ctime == 1755787524.0

    # Make child tables
    with database_sessionmaker() as session:
        processing_status = TimeDomainProcessingTable(
            processing_start=1756787524.0,
            processing_end=1756797524.0,
            processing_status="done",
            map=dmap,
        )

        pointing_residual = PointingResidualTable(
            ra_offset=1.2, dec_offset=-0.8, map=dmap
        )

        tod = TODDepthOneTable(
            obs_id="obs_1753486724_lati6_111",
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
            maps=[dmap],
        )

        pipeline_info = PipelineInformationTable(
            sotodlib_version="1.2.3",
            map_maker="minkasi",
            preprocess_info={"config": "test"},
            map=dmap,
        )

        sky_coverage = SkyCoverageTable(
            map=dmap,
            x=5,
            y=2,
        )

        session.add_all(
            [processing_status, pointing_residual, tod, pipeline_info, sky_coverage]
        )
        session.commit()

        proc_id = processing_status.processing_status_id
        point_id = pointing_residual.pointing_residual_id
        tod_id = tod.tod_id
        pipe_id = pipeline_info.pipeline_information_id
        sky_id = sky_coverage.patch_id

    # Get child tables back
    with database_sessionmaker() as session:
        proc = session.get(TimeDomainProcessingTable, proc_id)
        point = session.get(PointingResidualTable, point_id)
        tod = session.get(TODDepthOneTable, tod_id)
        pipe = session.get(PipelineInformationTable, pipe_id)
        sky = session.get(SkyCoverageTable, sky_id)

    assert proc.processing_status_id == proc_id
    assert proc.map_id == map_id
    assert proc.processing_start == 1756787524.0
    assert proc.processing_end == 1756797524.0
    assert proc.processing_status == "done"

    assert point.pointing_residual_id == point_id
    assert point.map_id == map_id
    assert point.ra_offset == 1.2
    assert point.dec_offset == -0.8

    assert tod.tod_id == tod_id
    assert tod.pwv == 0.7
    assert tod.obs_id == "obs_1753486724_lati6_111"
    assert tod.ctime == 1755787524.0
    assert tod.start_time == 1755687524.0
    assert tod.stop_time == 1755887524.0
    assert tod.nsamples == 28562
    assert tod.telescope == "lat"
    assert tod.telescope_flavor == "lat"
    assert tod.tube_slot == "i6"
    assert tod.tube_flavor == "mf"
    assert tod.frequency == "150"
    assert tod.scan_type == "ops"
    assert tod.subtype == "cmb"
    assert tod.wafer_count == 3
    assert tod.duration == 100000
    assert tod.az_center == 180.0
    assert tod.az_throw == 90.0
    assert tod.el_center == 50.0
    assert tod.el_throw == 0.0
    assert tod.roll_center == 0.0
    assert tod.roll_throw == 0.0
    assert tod.wafer_slots_list == "ws0,ws1,ws2"
    assert tod.stream_ids_list == "ufm_mv25,ufm_mv26,ufm_mv11"

    assert pipe.pipeline_information_id == pipe_id
    assert pipe.map_id == map_id
    assert pipe.sotodlib_version == "1.2.3"
    assert pipe.map_maker == "minkasi"
    assert pipe.preprocess_info == {"config": "test"}

    assert sky.patch_id == sky_id
    assert sky.x == "5"
    assert sky.y == "2"

    # Check bad map ID raises ValueError
    with pytest.raises(ValueError):
        with database_sessionmaker() as session:
            result = session.get(DepthOneMapTable, 999999)
            if result is None:
                raise ValueError("Map ID does not exist")


def test_add_remove_child_tables(database_sessionmaker):
    # Create a depth one map
    with database_sessionmaker() as session:
        dmap = DepthOneMapTable(
            map_name="myDepthOne2",
            map_path="/PATH/TO/DEPTH/ONE2",
            tube_slot="OTi1",
            frequency="f090",
            ctime=1755787524.0,
            start_time=1755687524.0,
            stop_time=1755887524.0,
        )

        processing_status = TimeDomainProcessingTable(
            processing_start=1756787524.0,
            processing_end=1756797524.0,
            processing_status="done",
            map=dmap,
        )

        pointing_residual = PointingResidualTable(
            ra_offset=1.2, dec_offset=-0.8, map=dmap
        )

        tod = TODDepthOneTable(
            obs_id="obs_1753486724_lati6_111",
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
            maps=[dmap],
        )

        pipeline_info = PipelineInformationTable(
            sotodlib_version="1.2.3",
            map_maker="minkasi",
            preprocess_info={"config": "test"},
            map=dmap,
        )

        sky_coverage = SkyCoverageTable(
            map=dmap,
            x=5,
            y=2,
        )

        session.add_all(
            [
                dmap,
                processing_status,
                pointing_residual,
                tod,
                pipeline_info,
                sky_coverage,
            ]
        )
        session.commit()

        dmap_id = dmap.map_id
        proc_id = processing_status.processing_status_id
        point_id = pointing_residual.pointing_residual_id
        tod_id = tod.tod_id
        pipe_id = pipeline_info.pipeline_information_id
        sky_id = sky_coverage.patch_id

    # Check the cascades work
    with database_sessionmaker() as session:
        x = session.get(DepthOneMapTable, dmap_id)
        session.delete(x)
        session.commit()

    with pytest.raises(ValueError):
        with database_sessionmaker() as session:
            x = session.get(TimeDomainProcessingTable, proc_id)
            if x is None:
                raise ValueError("Not found")

    with pytest.raises(ValueError):
        with database_sessionmaker() as session:
            x = session.get(PointingResidualTable, point_id)
            if x is None:
                raise ValueError("Not found")

    with database_sessionmaker() as session:
        tod = session.get(TODDepthOneTable, tod_id)
        assert tod is not None

    with pytest.raises(ValueError):
        with database_sessionmaker() as session:
            x = session.get(PipelineInformationTable, pipe_id)
            if x is None:
                raise ValueError("Not found")

    with pytest.raises(ValueError):
        with database_sessionmaker() as session:
            x = session.get(SkyCoverageTable, sky_id)
            if x is None:
                raise ValueError("Not found")


def test_create_atomic_map_coadd(database_sessionmaker):
    # Create a daily (child) coadd
    with database_sessionmaker() as session:
        data = AtomicMapCoaddTable(
            coadd_name="myDailyCoadd",
            prefix_path="/PATH/TO/DAILY/COADD",
            platform="satp3",
            interval="daily",
            start_time=1755604800.0,
            stop_time=1755691200.0,
            freq_channel="f090",
            geom_file_path="/PATH/TO/GEOM/FILE",
            split_label="full",
        )

        session.add(data)
        session.commit()
        session.refresh(data)

        daily_coadd_id = data.coadd_id

    # Get daily coadd back
    with database_sessionmaker() as session:
        cmap = session.get(AtomicMapCoaddTable, daily_coadd_id)

    assert cmap.coadd_id == daily_coadd_id
    assert cmap.coadd_name == "myDailyCoadd"
    assert cmap.prefix_path == "/PATH/TO/DAILY/COADD"
    assert cmap.platform == "satp3"
    assert cmap.interval == "daily"
    assert cmap.start_time == 1755604800.0
    assert cmap.stop_time == 1755691200.0
    assert cmap.freq_channel == "f090"
    assert cmap.geom_file_path == "/PATH/TO/GEOM/FILE"
    assert cmap.split_label == "full"

    # Make child atomic table
    with database_sessionmaker() as session:
        atomic_map = AtomicMapTable(
            obs_id="obs_1755643930_satp3_1111111",
            telescope="satp3",
            freq_channel="f090",
            wafer="ws0",
            ctime=1755643932,
            split_label="full",
            map_path=None,
            ivar_path=None,
            valid=True,
            split_detail="",
            prefix_path="PATH/TO/ATOMIC/MAP",
            elevation=59.9997,
            azimuth=290.9026,
            pwv=None,
            dpwv=None,
            total_weight_qu=660616773042064.2,
            mean_weight_qu=4206115923.380497,
            median_weight_qu=3255646486.1875,
            leakage_avg=None,
            noise_avg=None,
            ampl_2f_avg=None,
            gain_avg=None,
            tau_avg=None,
            f_hwp=None,
            roll_angle=0.0117,
            scan_speed=None,
            scan_acc=None,
            sun_distance=69.36016359440542,
            ambient_temperature=None,
            uv=None,
            ra_center=None,
            dec_center=None,
            number_dets=568,
            moon_distance=None,
            wind_speed=None,
            wind_direction=None,
            rqu_avg=None,
            coadds=[cmap],
        )

        session.add(atomic_map)
        session.commit()

        atomic_map_id = atomic_map.atomic_map_id

    # Get atomic table back
    with database_sessionmaker() as session:
        atomic = session.get(AtomicMapTable, atomic_map_id)
        atomic_coadds = atomic.coadds
        
    assert atomic.atomic_map_id == atomic_map_id
    assert atomic.obs_id == "obs_1755643930_satp3_1111111"
    assert atomic.telescope == "satp3"
    assert atomic.freq_channel == "f090"
    assert atomic.wafer == "ws0"
    assert atomic.ctime == 1755643932
    assert atomic.split_label == "full"
    assert atomic.map_path == None
    assert atomic.ivar_path == None
    assert atomic.valid == True
    assert atomic.split_detail == ""
    assert atomic.prefix_path == "PATH/TO/ATOMIC/MAP"
    assert atomic.elevation == 59.9997
    assert atomic.azimuth == 290.9026
    assert atomic.pwv == None
    assert atomic.dpwv == None
    assert atomic.total_weight_qu == 660616773042064.2
    assert atomic.mean_weight_qu == 4206115923.380497
    assert atomic.median_weight_qu == 3255646486.1875
    assert atomic.leakage_avg == None
    assert atomic.noise_avg == None
    assert atomic.ampl_2f_avg == None
    assert atomic.gain_avg == None
    assert atomic.tau_avg == None
    assert atomic.f_hwp == None
    assert atomic.roll_angle == 0.0117
    assert atomic.scan_speed == None
    assert atomic.scan_acc == None
    assert atomic.sun_distance == 69.36016359440542
    assert atomic.ambient_temperature == None
    assert atomic.uv == None
    assert atomic.ra_center == None
    assert atomic.dec_center == None
    assert atomic.number_dets == 568
    assert atomic.moon_distance == None
    assert atomic.wind_speed == None
    assert atomic.wind_direction == None
    assert atomic.rqu_avg == None
    
    assert atomic_coadds[0].coadd_id == daily_coadd_id
    
    # Create a weekly (parent) coadd
    with database_sessionmaker() as session:
        data = AtomicMapCoaddTable(
            coadd_name="myWeeklyCoadd",
            prefix_path="/PATH/TO/WEEKLY/COADD",
            platform="satp3",
            interval="weekly",
            start_time=1755432000.0,
            stop_time=1756036800.0,
            freq_channel="f090",
            geom_file_path="/PATH/TO/GEOM/FILE",
            split_label="full",
            child_coadds=[cmap]
        )

        session.add(data)
        session.commit()
        session.refresh(data)

        weekly_coadd_id = data.coadd_id

    # Get weekly coadd map back
    with database_sessionmaker() as session:
        cmap2 = session.get(AtomicMapCoaddTable, weekly_coadd_id)
        weekly_child_coadds = cmap2.child_coadds
        
    assert cmap2.coadd_id == weekly_coadd_id
    assert weekly_child_coadds[0].coadd_id == daily_coadd_id
    
    # Check daily coadd has weekly coadd as parent
    with database_sessionmaker() as session:
        cmap = session.get(AtomicMapCoaddTable, daily_coadd_id)
        daily_parent_coadds = cmap.parent_coadds
        
    assert daily_parent_coadds[0].coadd_id == weekly_coadd_id

    # Check bad map ID raises ValueError
    with pytest.raises(ValueError):
        with database_sessionmaker() as session:
            result = session.get(AtomicMapCoaddTable, 999999)
            if result is None:
                raise ValueError("Map ID does not exist")

                
def test_add_remove_atomic_map_coadd(database_sessionmaker):
    # Create daily and weekly coadds
    with database_sessionmaker() as session:
        daily = AtomicMapCoaddTable(
            coadd_name="myDailyCoadd",
            prefix_path="/PATH/TO/DAILY/COADD",
            platform="satp3",
            interval="daily",
            start_time=1755604800.0,
            stop_time=1755691200.0,
            freq_channel="f090",
            geom_file_path="/PATH/TO/GEOM/FILE",
            split_label="full",
        )

        weekly = AtomicMapCoaddTable(
            coadd_name="myWeeklyCoadd",
            prefix_path="/PATH/TO/WEEKLY/COADD",
            platform="satp3",
            interval="weekly",
            start_time=1755432000.0,
            stop_time=1756036800.0,
            freq_channel="f090",
            geom_file_path="/PATH/TO/GEOM/FILE",
            split_label="full",
            child_coadds=[daily]
        )

        session.add_all(
            [
                daily,
                weekly,
            ]
        )
        session.commit()
        
        daily_coadd_id = daily.coadd_id
        weekly_coadd_id = weekly.coadd_id
    
    # Remove weekly coadd and check daily coadd parents
    with database_sessionmaker() as session:
        x = session.get(AtomicMapCoaddTable, weekly_coadd_id)
        session.delete(x)
        session.commit()
        
    with pytest.raises(ValueError):
        with database_sessionmaker() as session:
            daily = session.get(AtomicMapCoaddTable, daily_coadd_id)
            if len(daily.parent_coadds) == 0:
                raise ValueError("Daily map has no parent coadds")
    
    # Check in reverse
    with database_sessionmaker() as session:
        weekly2 = AtomicMapCoaddTable(
            coadd_name="myWeeklyCoadd2",
            prefix_path="/PATH/TO/WEEKLY/COADD",
            platform="satp3",
            interval="weekly",
            start_time=1755432000.0,
            stop_time=1756036800.0,
            freq_channel="f090",
            geom_file_path="/PATH/TO/GEOM/FILE",
            split_label="full",
            child_coadds=[daily]
        )

        session.add(weekly2)
        session.commit()

        weekly2_coadd_id = weekly2.coadd_id
        
    with database_sessionmaker() as session:
        x = session.get(AtomicMapCoaddTable, daily_coadd_id)
        session.delete(x)
        session.commit()
        
    with pytest.raises(ValueError):
        with database_sessionmaker() as session:
            weekly2 = session.get(AtomicMapCoaddTable, weekly2_coadd_id)
            if len(weekly2.child_coadds) == 0:
                raise ValueError("Weekly map has no child coadds")