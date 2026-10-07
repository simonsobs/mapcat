from datetime import datetime, timezone

from mapcat.database import PlanetMapFitTable, PlanetMapTable, PlanetTodFitTable


def test_build_obslists(database_sessionmaker):
    # Make some planet maps
    with database_sessionmaker() as session:
        data1 = PlanetMapTable(
            obs_id="obs_1736469509_satp3_1111111",
            telescope="satp3",
            freq_channel="f150",
            wafer="ws0",
            source='jupiter',
            ctime=datetime.fromtimestamp(1755787524.0, tz=timezone.utc),
        )
        data1.hit_path = "/path/to/hit/file1"
        data1.map_path = "/path/to/hit/file2"
        data1.proc = ['hoge1', 'hoge2']
        data1.detnum = [10, 20]
        data1.detid = ['det1', 'det2']
        mapfit1 = PlanetMapFitTable()
        mapfit1.amplitude = 1
        mapfit1.xo = 0
        mapfit1.yo = 0
        mapfit1.sigmax = 1
        mapfit1.sigmay = 1
        mapfit1.theta = 0
        mapfit1.redchit = 1
        mapfit1.mq = 0.1
        mapfit1.d0q = 0.1
        mapfit1.d1q = 0.1
        mapfit1.sigmaq = 0.1
        mapfit1.redchiq = 1
        mapfit1.mu = 0.2
        mapfit1.d0u = 0.2
        mapfit1.d1u = 0.2
        mapfit1.sigmau = 0.2
        mapfit1.redchiu = 1.1

        data1.fit = mapfit1

        
        data2 = PlanetMapTable(
            obs_id="obs_1736469509_satp1_1111111",
            telescope="satp1",
            freq_channel="f090",
            wafer="ws1",
            source='saturn',
            ctime=datetime.fromtimestamp(1755787530.0, tz=timezone.utc),
        )
        data2.proc = ['hoge12', 'hoge2']
        data2.detnum = [12, 22]
        data2.detid = ['det12', 'det22']
                
        mapfit2 = PlanetMapFitTable()
        mapfit2.amplitude = 1
        mapfit2.xo = 0
        mapfit2.yo = 0
        mapfit2.sigmax = 1
        mapfit2.sigmay = 1
        mapfit2.theta = 0
        mapfit2.redchit = 1
        mapfit2.mq = 0.2
        mapfit2.d0q = 0.2
        mapfit2.d1q = 0.2
        mapfit2.sigmaq = 0.2
        mapfit2.redchiq = 2
        mapfit2.mu = 0.3
        mapfit2.d0u = 0.3
        mapfit2.d1u = 0.3
        mapfit2.sigmau = 0.3
        mapfit2.redchiu = 3

        data2.fit = mapfit2

        session.add(data1)
        session.commit()
        session.refresh(data1)

        session.add(data2)
        session.commit()
        session.refresh(data2)

        key1 = {
            "obs_id": data1.obs_id,
            "telescope": data1.telescope,
            "freq_channel": data1.freq_channel,
            "wafer": data1.wafer,
            "source": data1.source,
        }

        key2 = {
            "obs_id": data2.obs_id,
            "telescope": data2.telescope,
            "freq_channel": data2.freq_channel,
            "wafer": data2.wafer,
            "source": data2.source,
        }
    # Get depth one map back
    with database_sessionmaker() as session:
        data1 = session.get(PlanetMapTable, key1)
        data2 = session.get(PlanetMapTable, key2)

    with database_sessionmaker() as session:
        x1 = session.get(PlanetMapTable, key1)
        session.delete(x1)
        session.commit()
        assert x1 is not None


    with database_sessionmaker() as session:
        todfit1 = PlanetTodFitTable(
            obs_id="obs_1736469509_satp3_1111111",
            telescope="satp3",
            freq_channel="f150",
            wafer="ws0",
            source="jupiter",
            detid="det1",
            ctime=datetime.fromtimestamp(
                1755787524.0,
                tz=timezone.utc,
            ),
            amplitude=1.0,
            xo=0.0,
            yo=0.0,
            sigmax=1.0,
            sigmay=1.0,
            theta=0.0,
            chisq=1.0,
            dof=100,
        )

        todfit2 = PlanetTodFitTable(
            obs_id="obs_1736469509_satp1_1111111",
            telescope="satp1",
            freq_channel="f090",
            wafer="ws1",
            source="saturn",
            detid="det12",
            ctime=datetime.fromtimestamp(
                1755787526.0,
                tz=timezone.utc,
            ),
            amplitude=1.1,
            xo=0.1,
            yo=0.1,
            sigmax=1.1,
            sigmay=1.1,
            theta=0.1,
            chisq=1.1,
            dof=101,
        )

        session.add(todfit1)
        session.commit()
        session.refresh(todfit1)

        session.add(todfit2)
        session.commit()
        session.refresh(todfit2)

        key_tod1 = {
            "obs_id": todfit1.obs_id,
            "telescope": todfit1.telescope,
            "freq_channel": todfit1.freq_channel,
            "wafer": todfit1.wafer,
            "source": todfit1.source,
            "detid": todfit1.detid,
        }
        
    with database_sessionmaker() as session:
        y1 = session.get(PlanetTodFitTable, key_tod1)

    with database_sessionmaker() as session:
        y1 = session.get(PlanetTodFitTable, key_tod1)
        session.delete(y1)
        session.commit()
        assert y1 is not None