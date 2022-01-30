import os
from datetime import datetime, date
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import rasterio as rio
from rasterio import plot
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
    imagePath = './downloads/S2A_MSIL2A_20220128T101301_N0400_R022_T33UUU_20220128T133019.SAFE/GRANULE/L2A_T33UUU_A034482_20220128T101258/IMG_DATA/R10m/'
    band2 = rio.open(
        imagePath+'T33UUU_20220128T101301_B02_10m.jp2', driver='JP2OpenJPEG')  # blue
    band3 = rio.open(
        imagePath+'T33UUU_20220128T101301_B03_10m.jp2', driver='JP2OpenJPEG')  # green
    band4 = rio.open(
        imagePath+'T33UUU_20220128T101301_B04_10m.jp2', driver='JP2OpenJPEG')  # red
    band8 = rio.open(
        imagePath+'T33UUU_20220128T101301_B08_10m.jp2', driver='JP2OpenJPEG')  # nir

    trueColor = rio.open('./processed/SentinelTrueColor2.tiff', 'w', driver='Gtiff',
                         width=band4.width, height=band4.height,
                         count=3,
                         crs=band4.crs,
                         transform=band4.transform,
                         dtype=band4.dtypes[0]
                         )

    trueColor.write(band2.read(1), 3)  # blue
    trueColor.write(band3.read(1), 2)  # green
    trueColor.write(band4.read(1), 1)  # red
    trueColor.close()

    falseColor = rio.open('./processed/SentinelFalseColor.tiff', 'w', driver='Gtiff',
                          width=band2.width, height=band2.height,
                          count=3,
                          crs=band2.crs,
                          transform=band2.transform,
                          dtype='uint16'
                          )

    falseColor.write(band3.read(1), 3)  # Blue
    falseColor.write(band4.read(1), 2)  # Green
    falseColor.write(band8.read(1), 1)  # Red
    falseColor.close()


def show_histogram(path):
    trueColor = rio.open(path)
    plot.show_hist(trueColor, bins=50, lw=0.0, stacked=False,
                   alpha=0.3, histtype='stepfilled', title="Histogram")


# query_data()
# download_product(uuid="fc6655b2-83b0-42e2-9a5e-12b0fda57ea8")
# create_rgb_image()
# show_histogram('./processed/SentinelFalseColor.tiff')
