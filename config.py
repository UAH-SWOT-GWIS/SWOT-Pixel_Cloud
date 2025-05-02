import os

from dotenv import load_dotenv

######################################
# EarthAccess uses the environment variables for login, so EarthData credentials are kept in the .env file
######################################
load_dotenv()


s3BucketName = 'swot-data-bucket'
s3ShapeFolder = 'swot-data-points'
aws_access_key_id = 'PLACEHOLDER'
aws_secret_access_key = 'PLACEHOLDER'

short_name = 'SWOT_L2_HR_PIXC_2.0'
data_ver = "2.0"
granule_list = [
    "147_210R",
    "147_209L",
    "147_209R",
    "466_100L"
    ]

W_CLASS = {
    1: 'land',
    2: 'land_near_water',
    3: 'water_near_land',
    4: 'open_water',
    5: 'dark_water',
    6: 'low_coh_water_near_land',
    7: 'open_low_coh_water',
    }

# You can add attributes to pull from the NetCDF files here in <key> : <value> format (each pair must be separated by a comma)
# The <key> is the full attribute name in the NetCDF file. This can be found in the data product description
# the <value> is the name that the attribute will be given in the ShapeFile. It MUST be 10 characters or less, otherwise the ShapeFile will fail to write
# Currently, you can only fetch attributes that are indexed by "point" (please see the list of attributes in the data product description). This will cover most attributes in the pixel_cloud group
pixel_attributes = {
    "classification": "class",
    }

