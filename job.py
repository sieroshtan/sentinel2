import subprocess
from os import makedirs, path, listdir
from db import database
from regex import params_of_granule


class Job(object):

    def __init__(self, sandbox):
        self._sandbox = sandbox

    java_command = "java -jar ~/ProductDownload/ProductDownload.jar --sensor S2 --out {out} --tiles {scene} --startdate {startdate} --enddate {enddate} --store AWS --cloudpercentage 50 --user spatialhast --password sentinelhub55"
    sen2cor_command = "L2A_Process --resolution=10 {scene}"

    granule_name = r'^S2A_USER_MSI_L2A_TL_SGS__(?P<date>[0-9]{8})T(\d{6})_A(\d{6})_(?P<scene>[A-Z0-9]{6})_N02\.04$'
    # granule_name = r'^S2A_OPER_MSI_L1C_TL_SGS__(?P<date>[0-9]{8})T(\d{6})_A(\d{6})_(?P<scene>[A-Z0-9]{6})_N02\.04$'
    # S2A_USER_MSI_L2A_TL_SGS__20160621T141023_A005209_T37UCR_N02.04

    def run(self, date_from, date_to):
        with self._sandbox as sandbox:
            self._download_data_in(date_from, date_to, sandbox)
            # l1a_files = sandbox.get_filepaths(startswith='S2A_OPER')
            # [self._l2a_process(filepath) for filepath in l1a_files]

            l2a_files = sandbox.get_filepaths(startswith='S2A_USER')
            print("l2a_files", l2a_files)
            [self._create_tile(filepath) for filepath in l2a_files]

    def _download_data_in(self, date_from, date_to, sandbox):
        cursor = database.execute_sql(
            "select s2_index.name from akleshnin_farm_boundary_geopoints_poly inner join s2_index on ST_Intersects(akleshnin_farm_boundary_geopoints_poly.geom, s2_index.wkb_geometry) where farm_boundary_id = 346"
        )

        for row in cursor.fetchall():
            print subprocess.Popen(
                self.java_command.format(scene='37UCR', out=sandbox.relpath, startdate=date_from, enddate=date_to),
                shell=True, stdout=subprocess.PIPE
            ).stdout.read()

    def _l2a_process(self, filepath):
        print("_l2a_process start", filepath)
        print subprocess.Popen(
            self.sen2cor_command.format(scene=filepath),
            shell=True, stdout=subprocess.PIPE
        ).stdout.read()
        print("_l2a_process end", filepath)

    def _create_tile(self, filepath):
        granula_root_folder = path.abspath(filepath)

        print("granula_root_folder", granula_root_folder)

        granule_folder = [path.basename(f) for f in listdir(granula_root_folder + '/GRANULE') if 'S2A_USER' in f][0]

        print(granule_folder)

        date, scene = params_of_granule(granule_folder, self.granule_name)

        print("date", date, "scene", scene)

        makedirs('tiles/S2L2A_tile_{date}_{scene}'.format(date=date, scene=scene))
