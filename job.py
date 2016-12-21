import subprocess
from db import database


class Job(object):
    def run(self, date_from, date_to):
        cursor = database.execute_sql('select s2_index.name from akleshnin_farm_boundary_geopoints_poly inner join s2_index on ST_Intersects(akleshnin_farm_boundary_geopoints_poly.geom, s2_index.wkb_geometry) where farm_boundary_id = 346')

        for row in cursor.fetchall():
            print subprocess.Popen(
                "java -jar /home/opengeo/ProductDownload/ProductDownload.jar --sensor S2 --out /home/opengeo/alexs/s2data --tiles {scene} --startdate {startdate} --enddate {enddate} --store AWS --cloudpercentage 50 --user spatialhast --password sentinelhub55".format(
                    scene=row[0], startdate=date_from, enddate=date_to), shell=True,
                stdout=subprocess.PIPE).stdout.read()
