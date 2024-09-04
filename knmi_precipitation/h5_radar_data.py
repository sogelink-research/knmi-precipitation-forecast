import h5py
import os

from osgeo import gdal
from pyproj import Proj, Transformer
from knmi_precipitation.utils import value_to_mm_hr, h5_datetime_to_datetime

os.environ['PROJ_IGNORE_CELESTIAL_BODY'] = 'TRUE'


class H5RadarData:
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File {file_path} not found')

        self.path = file_path
        self.file = h5py.File(file_path, 'r')
        self.geo_row_offset = self.file['geographic'].attrs['geo_row_offset'][0]
        self.geo_number_columns = self.file['geographic'].attrs['geo_number_columns'][0]
        self.geo_number_rows = self.file['geographic'].attrs['geo_number_rows'][0]
        proj_string = self.file['geographic']['map_projection'].attrs['projection_proj4_params'].decode(
            'utf-8')
        self.proj_knmi = Proj(proj_string)
        self.proj_wgs84 = Proj("EPSG:4326")
        self.proj_transformer_wgs84_knmi = Transformer.from_proj(
            self.proj_wgs84, self.proj_knmi, always_xy=True)
        self.proj_transformer_knmi_wgs84 = Transformer.from_proj(
            self.proj_knmi, self.proj_wgs84, always_xy=True)
        self.image_data = {}

    def get_image_data(self, image_name):
        if self.image_data.get(image_name) is not None:
            return self.image_data[image_name]

        self.image_data[image_name] = self.file[image_name]['image_data'][:]

        return self.image_data[image_name]

    def lng_lat_to_knmi(self, lng, lat):
        x, y = self.proj_transformer_wgs84_knmi.transform(lng, lat)
        y = (-self.geo_row_offset - y)

        return x, y

    def knmi_to_lng_lat(self, x, y):
        y = -y - self.geo_row_offset
        lng, lat = self.proj_transformer_knmi_wgs84.transform(x, y)

        return lng, lat

    def knmi_to_frame(self, x, y):
        col = round(x)
        row = round(y)

        return row, col

    def frame_to_knmi(self, row, col):
        x = col
        y = row

        return x, y

    def get_mm_hr_from_lon_lat(self, image_name, lng, lat):
        value = self.get_value_from_lon_lat(image_name, lng, lat)

        return value_to_mm_hr(value)

    def get_value_from_lon_lat(self, image_name, lng, lat):
        x, y = self.lng_lat_to_knmi(lng, lat)
        row, col = self.knmi_to_frame(x, y)
        data = self.get_image_data(image_name)

        return data[row][col]

    def get_mm_hr_from_frame(self, image_name, row, col):
        value = self.get_value_from_frame(image_name, row, col)

        return value_to_mm_hr(value)

    def get_value_from_frame(self, image_name, row, col):
        data = self.get_image_data(image_name)
        return data[row][col]

    def get_image_infos(self):
        files = []

        for key in self.file:
            if 'image' in key:
                date_string = self.file[key].attrs['image_datetime_valid'].decode(
                    'utf-8')
                files.append({
                    'name': key,
                    'datetime': h5_datetime_to_datetime(date_string)
                })

        return files

    def export_geotiff(self, image_name, output_filename):
        data = self.get_image_data(image_name)
        temp_filename = f'{output_filename}_temp'
        output_filename = f'{output_filename}'

        # change the original projection string to meters
        knmi_proj_string_meter = '+proj=stere +lat_0=90 +lon_0=0 +lat_ts=60 +a=6378140 +b=6356750 +x_0=0 y_0=0 +units=m'
        proj_knmi = Proj(knmi_proj_string_meter)

        driver = gdal.GetDriverByName('GTiff')
        temp_raster = driver.Create(
            temp_filename, int(self.geo_number_columns), int(self.geo_number_rows), 1, gdal.GDT_Float32)

        temp_raster.SetGeoTransform(
            (0, 1000, 0, -self.geo_row_offset * 1000, 0, -1000))
        temp_raster.SetProjection(proj_knmi.crs.to_wkt())
        temp_raster.GetRasterBand(1).WriteArray(data)
        temp_raster.GetRasterBand(1).SetNoDataValue(0)
        temp_raster.FlushCache()

        # Perform the reprojection using gdal.Warp
        gdal.Warp(output_filename, temp_raster,
                  srcSRS=proj_knmi.crs.to_wkt(),
                  dstSRS=self.proj_wgs84.crs.to_wkt(), format='GTiff')

        # Clean up
        del temp_raster
        driver.Delete(temp_filename)
