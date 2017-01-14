import subprocess
import os
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
            l1a_files = sandbox.get_filepaths(startswith='S2A_OPER')
            [self._l2a_process(filepath) for filepath in l1a_files]

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
        granula_root_folder = os.path.abspath(filepath)

        print("granula_root_folder", granula_root_folder)

        granule_folder_path = [f for f in os.listdir(granula_root_folder + '/GRANULE') if 'S2A_USER' in f][0]

        print(granule_folder_path)

        date, scene = params_of_granule(os.path.basename(granule_folder_path), self.granule_name)

        print("date", date, "scene", scene)

        tile_path_string = 'tiles/S2L2A_tile_{date}_{scene}'.format(date=date, scene=scene)

        os.makedirs(tile_path_string)

        r10m_path = os.path.join(granule_folder_path, 'IMG_DATA/R10m')
        r20m_path = os.path.join(granule_folder_path, 'IMG_DATA/R20m')

        print('r10m_path', r10m_path)
        print('r20m_path', r20m_path)

        r10m_files = [f for f in os.listdir(r10m_path) if f.endswith(('B04_10m.jp2', 'B08_10m.jp2'))]
        r20m_files = [f for f in os.listdir(r20m_path) if f.endswith(('B11_20m.jp2', 'B12_20m.jp2'))]

        print('r10m_files', r10m_files)
        print('r20m_files', r20m_files)

        needed_files = r10m_files + r20m_files

        print('needed_files', needed_files)

        [os.rename(f, os.path.join(tile_path_string, os.path.basename(f))) for f in needed_files]

        [os.rename(f, os.path.join(os.path.dirname(f), os.path.basename(f)[-11:-8], '.jp2')) for f in os.listdir(tile_path_string) if f.endswith('.jp2')]
