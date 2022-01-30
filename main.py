import os
from datetime import datetime, date
import uuid
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import rasterio as rio
from dotenv import load_dotenv
import pprint

load_dotenv()

user = os.environ.get('SENTINEL_USER')
password = os.environ.get('SENTINEL_PASSWORD')


def query_data(start_date=date(2021, 5, 1), end_date=date(2021, 10, 1)):
    api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
    footprint = geojson_to_wkt(read_geojson('./berlin_tiergarten.geojson'))
    producttypes = ['S2MSI1C', 'S2MSI2A', 'S2MSI2Ap']
    producttype = producttypes[1]
    cloudcoverpercentage = (0, 30)
    date = (start_date, end_date)

    products = api.query(footprint,
                         date=date,
                         platformname='Sentinel-2',
                         producttype=producttype,
                         orbitdirection='ASCENDING',
                         cloudcoverpercentage=cloudcoverpercentage,
                         limit=40)

    pprint.pprint(products, sort_dicts=False)


def download_product(uuid):
    if not uuid:
        print("Please provide an UUID")
        return

    api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
    api.download(id=uuid, directory_path='./downloads')


def create_rgb_image():
    R10 = './downloads/S2A_MSIL2A_20220128T101301_N0400_R022_T33UUU_20220128T133019.SAFE/GRANULE/L2A_T33UUU_A034482_20220128T101258/IMG_DATA/R10m/'

    b4 = rio.open(R10+'T33UUU_20220128T101301_B04_10m.jp2',
                  driver='JP2OpenJPEG')
    b3 = rio.open(R10+'T33UUU_20220128T101301_B03_10m.jp2',
                  driver='JP2OpenJPEG')
    b2 = rio.open(R10+'T33UUU_20220128T101301_B02_10m.jp2',
                  driver='JP2OpenJPEG')

    with rio.open('./processed/RGB.tiff', 'w', driver='Gtiff', width=b4.width, height=b4.height,
                  count=3, crs=b4.crs, transform=b4.transform, dtype=b4.dtypes[0]) as rgb:
        rgb.write(b2.read(1), 1)
        rgb.write(b3.read(1), 2)
        rgb.write(b4.read(1), 3)
        rgb.close()


# query_data()
# download_product(uuid="fc6655b2-83b0-42e2-9a5e-12b0fda57ea8")
# create_rgb_image()
