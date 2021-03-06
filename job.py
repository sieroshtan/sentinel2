import subprocess
import shutil
import os
from datetime import timedelta, datetime

from db import database
from models import SentinelScene
from geo_json_helper import createGeoJson

from osgeo import gdal


def _daterange(start_date, end_date):
    """
    Date range generator
    :param start_date:
    :param end_date:
    :return:
    """
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def _get_existing_dates(farm_id):
    """
    Return processed dates for a farm
    :param farm_id:
    :return:
    """
    return [entry.date for entry in SentinelScene.select().where(SentinelScene.farm_id == farm_id)]


class Job(object):
    """
    Main class job for download, converting, processing, etc.
    """

    def __init__(self, farm_id, sandbox):
        self._farm_id = farm_id
        self._sandbox = sandbox

    # folder for tiles saving
    tile_folder = os.path.join(os.path.expanduser('~'), 'tiles')

    # command templates
    CLI_DOWNLOAD = "java -jar ~/ProductDownload/ProductDownload.jar --sensor S2 --aws --out {out} --tiles {tiles} --startdate {date} --enddate {date} --store AWS --cloudpercentage 50"
    CLI_L1C_TO_L2A = "L2A_Process --resolution=10 {safe}"
    CLI_GDAL_TRANSLATE = "gdal_translate -co TILED=YES --config GDAL_CACHEMAX 500 {jp2} {tif}"
    CLI_NDVI = "gdal_calc.py -A {B08} -B {B04} --outfile={outfile} --calc=\"(A.astype(float) - B.astype(float))/(A.astype(float) + B.astype(float))\" --type=Float32"
    CLI_GDALBUILDVRT = "gdalbuildvrt -resolution highest -separate {vrt} {B08} {B11} {B12}"
    CLI_NMDI = "gdal_calc.py -A {vrt} --A_band=1 -B {vrt} --B_band=2 -C {vrt} --C_band=3 --outfile={outfile} --calc=\"(A.astype(float) - (B.astype(float) - C.astype(float)))/(A.astype(float) + (B.astype(float) - C.astype(float)))\" --type=Float32"
    CLI_GDALDEM = "gdaldem color-relief {input} {color} {output}"
    CLI_GDALWARP = "gdalwarp {rgb} {clip} -cutline {geojson} -crop_to_cutline -dstalpha"
    CLI_GDAL2TILES = "gdal2tiles.py -z 8-16 -v --webviewer=openlayers {input} {output}"

    def run(self, date_from, date_to):
        for farm in self._get_farms():
            farm_id = farm['farm_id']
            scene = farm['scene']
            polygon = farm['poly']

            existing_dates = _get_existing_dates(farm_id)

            for single_date in _daterange(date_from, date_to):
                if single_date in existing_dates:
                    print("Scene for {0} date already processed in the DB. Skipped.".format(single_date.strftime('%Y-%m-%d')))
                    continue

                print(farm_id, single_date)

                single_date_str = single_date.strftime('%Y%m%d')
                try:
                    with self._sandbox as sandbox:
                        params = {'out': sandbox.relpath, 'tiles': scene, 'date': single_date}
                        self._run_cli(self.CLI_DOWNLOAD, params)

                        # L1C_filepath = sandbox.get_filepath(pattern=r'^S2A_MSIL1C_{0}.*{1}.*\.SAFE$'.format(single_date_str, scene))
                        L1C_filepath = sandbox.get_filepath(pattern=r'^S2A_.*_MSIL1C_.*_{0}.*\.SAFE$'.format(single_date_str))

                        if not L1C_filepath:
                            raise BaseException

                        self.L1C_TO_L2A(L1C_filepath)

                        geo_json_path = os.path.join(self.tile_folder, str(farm_id), 'poly.geojson')
                        tilepath = self._create_tile_folder(farm_id, single_date_str)

                        if not os.path.exists(geo_json_path):
                            createGeoJson(polygon, geo_json_path)

                        # L2A_filepath = sandbox.get_filepath(pattern=r'^S2A_MSIL2A_{0}.*{1}.*\.SAFE$'.format(single_date_str, scene))
                        L2A_filepath = sandbox.get_filepath(pattern=r'^S2A_.*_MSIL2A_.*{0}.*\.SAFE$'.format(single_date_str))

                        self._move_jp2_to_tilepath(L2A_filepath, sandbox.abspath)

                        [self._jp2_to_tif(os.path.join(sandbox.abspath, f)) for f in os.listdir(sandbox.abspath) if f.endswith('.jp2')]

                        params = {
                            'B08': os.path.join(sandbox.abspath, 'B08.tif'),
                            'B04': os.path.join(sandbox.abspath, 'B04.tif'),
                            'outfile': os.path.join(sandbox.abspath, 'ndvi.tif'),
                        }
                        self._run_cli(self.CLI_NDVI, params)

                        params = {
                            'vrt': os.path.join(sandbox.abspath, 'nmdi_vrt.tif'),
                            'B08': os.path.join(sandbox.abspath, 'B08.tif'),
                            'B11': os.path.join(sandbox.abspath, 'B11.tif'),
                            'B12': os.path.join(sandbox.abspath, 'B12.tif')
                        }
                        self._run_cli(self.CLI_GDALBUILDVRT, params)

                        params = {
                            'vrt': os.path.join(sandbox.abspath, 'nmdi_vrt.tif'),
                            'outfile': os.path.join(sandbox.abspath, 'nmdi.tif')
                        }
                        self._run_cli(self.CLI_NMDI, params)

                        params = {
                            'input': os.path.join(sandbox.abspath, 'ndvi.tif'),
                            'color': os.path.join(os.getcwd(), 'color_relief_ndvi.txt'),
                            'output': os.path.join(sandbox.abspath, 'ndvi_rgb.tif')
                        }
                        self._run_cli(self.CLI_GDALDEM, params)

                        params = {
                            'input': os.path.join(sandbox.abspath, 'nmdi.tif'),
                            'color': os.path.join(os.getcwd(), 'color_relief_nmdi.txt'),
                            'output': os.path.join(sandbox.abspath, 'nmdi_rgb.tif')
                        }
                        self._run_cli(self.CLI_GDALDEM, params)

                        params = {
                            'rgb': os.path.join(sandbox.abspath, 'ndvi_rgb.tif'),
                            'clip': os.path.join(sandbox.abspath, 'ndvi_clip.tif'),
                            'geojson': geo_json_path
                        }
                        self._run_cli(self.CLI_GDALWARP, params)

                        params = {
                            'rgb': os.path.join(sandbox.abspath, 'nmdi_rgb.tif'),
                            'clip': os.path.join(sandbox.abspath, 'nmdi_clip.tif'),
                            'geojson': geo_json_path
                        }
                        self._run_cli(self.CLI_GDALWARP, params)

                        params = {
                            'rgb': os.path.join(sandbox.abspath, 'ndvi.tif'),
                            'clip': os.path.join(sandbox.abspath, 'ndvi_clip_raw.tif'),
                            'geojson': geo_json_path
                        }
                        self._run_cli(self.CLI_GDALWARP, params)

                        params = {
                            'rgb': os.path.join(sandbox.abspath, 'nmdi.tif'),
                            'clip': os.path.join(sandbox.abspath, 'nmdi_clip_raw.tif'),
                            'geojson': geo_json_path
                        }
                        self._run_cli(self.CLI_GDALWARP, params)

                        ndvi_index, nmdi_index = self._get_ndvi_and_nmdi_indexes(
                            os.path.join(sandbox.abspath, 'ndvi_clip_raw.tif'),
                            os.path.join(sandbox.abspath, 'nmdi_clip_raw.tif')
                        )

                        if ndvi_index > 0 and nmdi_index > 0:  # skip scenes with zero indexes
                            SentinelScene.create(
                                farm_id=farm_id,
                                scene=scene,
                                date=single_date,
                                ndvi=ndvi_index,
                                nmdi=nmdi_index
                            )

                            params = {
                                'input': os.path.join(sandbox.abspath, 'ndvi_clip.tif'),
                                'output': os.path.join(tilepath, 'ndvi')
                            }
                            self._run_cli(self.CLI_GDAL2TILES, params)

                            params = {
                                'input': os.path.join(sandbox.abspath, 'nmdi_clip.tif'),
                                'output': os.path.join(tilepath, 'nmdi')
                            }
                            self._run_cli(self.CLI_GDAL2TILES, params)
                except:
                    # continue processing next date
                    continue

    def _get_farms(self):
        """
        Return farm geo data, like: scene id and polygon
        :return:
        """
        sql = "select farms.id, s2_index.name, ST_AsBinary(farms.polygon) from farms " \
              "inner join s2_index on ST_Intersects(farms.polygon, s2_index.wkb_geometry)"

        if self._farm_id:
            sql += " where farms.id = {0}".format(self._farm_id)

        cursor = database.execute_sql(sql)
        data = []
        for row in cursor.fetchall():
            data.append({
                'farm_id': row[0],
                'scene': row[1],
                'poly': row[2],
            })
        return data

    def L1C_TO_L2A(self, filepath):
        self._run_cli(self.CLI_L1C_TO_L2A, {'safe': filepath})

    def _create_tile_folder(self, farm_id, date_str):
        tilepath = os.path.join(self.tile_folder, str(farm_id), date_str)

        if os.path.exists(tilepath):
            shutil.rmtree(tilepath)
        os.makedirs(tilepath)

        return tilepath

    def _move_jp2_to_tilepath(self, L2A_filepath, tilepath):
        # granule_name = [f for f in os.listdir(os.path.join(L2A_filepath, 'GRANULE')) if f.startswith('L2A_')][0]
        granule_name = [f for f in os.listdir(os.path.join(L2A_filepath, 'GRANULE')) if f.startswith('S2A_USER_')][0]

        r10m_path = os.path.join(L2A_filepath, 'GRANULE', granule_name, 'IMG_DATA/R10m')
        r20m_path = os.path.join(L2A_filepath, 'GRANULE', granule_name, 'IMG_DATA/R20m')

        r10m_filepaths = [os.path.join(r10m_path, f) for f in os.listdir(r10m_path) if f.endswith(('B04_10m.jp2', 'B08_10m.jp2'))]
        r20m_filepaths = [os.path.join(r20m_path, f) for f in os.listdir(r20m_path) if f.endswith(('B11_20m.jp2', 'B12_20m.jp2'))]

        needed_files = r10m_filepaths + r20m_filepaths

        [os.rename(f, os.path.join(tilepath, os.path.basename(f)[-11:-8] + '.jp2')) for f in needed_files]  # prod
        # [shutil.copyfile(f, os.path.join(tilepath, os.path.basename(f)[-11:-8] + '.jp2')) for f in needed_files]  # dev

    def _jp2_to_tif(self, jp2_path):
        params = {'jp2': jp2_path, 'tif': jp2_path.replace('jp2', 'tif')}
        self._run_cli(self.CLI_GDAL_TRANSLATE, params)

    def _get_ndvi_and_nmdi_indexes(self, ndvi_tif, nmdi_tif):
        dataset = gdal.Open(ndvi_tif)
        band = dataset.GetRasterBand(1)
        band.SetNoDataValue(0)
        stats = band.ComputeStatistics(0)
        ndvi_index = stats[2]

        dataset = gdal.Open(nmdi_tif)
        band = dataset.GetRasterBand(1)
        band.SetNoDataValue(0)
        stats = band.ComputeStatistics(0)
        nmdi_index = stats[2]

        return ndvi_index, nmdi_index

    def _run_cli(self, command, params):
        print(command.format(**params))
        print subprocess.Popen(
            command.format(**params),
            shell=True, stdout=subprocess.PIPE
        ).stdout.read()
