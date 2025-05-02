import os
import traceback
import logging

import boto3
import netCDF4 as nc
import pandas as pd
import geopandas as gpd
import numpy as np

from shapely.geometry import Point
from zipfile import ZipFile
from config import s3BucketName, s3ShapeFolder, W_CLASS, pixel_attributes, aws_access_key_id, aws_secret_access_key
logger = logging.getLogger(__name__)

s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Subroutine for generating the ShapeFile with the desired categories
def make_shp(nc_fname, shp_name):
    data = nc.Dataset(nc_fname)
    
    pixel_group = data["pixel_cloud"]
    
    point_list = []
    longs = pixel_group["longitude"][:]
    lats = pixel_group["latitude"][:]
    
    heights = pixel_group["height"][:]
    geoids = pixel_group["geoid"][:]   
    
    adj_height = heights - geoids
    
    shp_dict = {
        'height': heights,
        'adj_height': adj_height,
        }
    
    for i in range(len(lats)):
        point_list.append(Point(longs[i], lats[i]))
        
    for key, val in pixel_attributes.items():
        temp_list = pixel_group[key][:]
        shp_dict[val] = temp_list
    
    shp_dict['geometry'] = point_list
    
    data.close()
    
    gdf = gpd.GeoDataFrame(shp_dict, crs="EPSG:4326")
    
    #Clean up unneeded list to keep overhead low. This was necessary for small EC2 instances
    del point_list
    del adj_height
    del geoids
    del heights
    del lats
    del longs
    
    if 'classification' in pixel_attributes:
        gdf['class_desc'] = gdf['class'].map(W_CLASS).astype('category')
    
    #Write to shapefile collection
    try:
        gdf.to_file(f"{shp_name}.shp")
    except Exception as e:
        logger.error(f"Error when creating ShapeFile: {str(e)}")
        logger.info(traceback.format_exc())
        return
    
    del gdf
    
    #Zip up the collection of files that make up a ShapeFile
    with ZipFile(f"{shp_name}.zip", 'w') as myzip:
        myzip.write(f"{shp_name}.shp")
        myzip.write(f"{shp_name}.cpg")
        myzip.write(f"{shp_name}.dbf")
        myzip.write(f"{shp_name}.prj")
        myzip.write(f"{shp_name}.shx")

# Subroutine for deleting the NetCDF and ShapeFile components after upload is complete      
def delete_files(file_name, shp_name):
    if os.path.exists(file_name):
        os.remove(file_name)
        
    if os.path.exists(f"{shp_name}.zip"):
        os.remove(f"{shp_name}.zip")
        
    if os.path.exists(f"{shp_name}.shp"):
        os.remove(f"{shp_name}.shp")
        os.remove(f"{shp_name}.cpg")
        os.remove(f"{shp_name}.dbf")
        os.remove(f"{shp_name}.prj")
        os.remove(f"{shp_name}.shx")

# Main process task
def process_shp(file_name, meta_data):
    # Switch these prints for logs?
    logger.info(f"Generating ShapeFile for {file_name}")
    	
    date_string = meta_data.get('date', 'unknown')
    shp_name = file_name[:-3]
    	
    if date_string != 'unknown':
        date_string = date_string[:-3]  # Get YYYY-MM format for storing the ShapeFiles
        
    s3_dir = f"{s3ShapeFolder}/{date_string}/{shp_name}.zip"
    	
    make_shp(file_name, shp_name)
    if not os.path.exists(f"{shp_name}.zip"):
        delete_files(file_name, shp_name)
        return
    
    try:
        # Try to upload the zipped ShapeFile. May need to adjust this to work in chunks
        query = s3.upload_file(f"{shp_name}.zip", s3BucketName, s3_dir)
        
        logger.info(f"Uploaded {shp_name}.zip to s3://{s3BucketName}/{s3ShapeFolder}/{date_string}/")
        delete_files(file_name, shp_name)
        
    except Exception as e:
        logger.error(f"Failed to upload {shp_name}.zip: {str(e)}")
        logger.info(traceback.format_exc())
        delete_files(file_name, shp_name)


