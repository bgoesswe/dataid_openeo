from nameko_sqlalchemy import DatabaseSession
from ..models import Base, Query
import sys
import numpy as np
from datetime import datetime
coords = [(10.288696, 45.935871), (12.189331, 46.905246)]

FACTOR_RESOLUTION = 1000


def reproject(latitude, longitude):
    """Returns the x & y coordinates in meters using a sinusoidal projection"""
    from math import pi, cos, radians
    earth_radius = 6371009 # in meters
    lat_dist = pi * earth_radius / 180.0

    y = [lat * lat_dist for lat in latitude]
    x = [long * lat_dist * cos(radians(lat))
                for lat, long in zip(latitude, longitude)]
    return x, y


def area_of_polygon(x, y):
    """Calculates the area of an arbitrary polygon given its verticies"""
    area = 0.0
    for i in range(-1, len(x)-1):
        area += x[i] * (y[i+1] - y[i-1])
    return abs(area) / 2.0


def generate_area(lon1, lat1, lon2, lat2, date_start, date_end):

    longitude = [lon1, lon1, lon2, lon2]
    latitude = [lat1, lat2, lat1, lat2]

    x, y = reproject(longitude, latitude)
    # x2, y2 = reproject(lon2, lat2)

    width = int((((x[0]-x[1])**2)**0.5)/FACTOR_RESOLUTION)
    height = int((((y[0]-y[3])**2)**0.5)/FACTOR_RESOLUTION)
    # area = area_of_polygon(x, y)

    start = datetime.strptime(date_start, "%Y-%m-%d")
    end = datetime.strptime(date_end, "%Y-%m-%d")

    daterange = end-start

    area = np.ones((width, height, daterange.days))

    return area


def set_no_data(data, cur, should):
    '''Set no data value'''

    data[data == cur] = should
    return data


def calc_ndvi(red, nir):
    '''Returns ndvi for given red and nir band (no data is set to 2, ndvi in range [-1, 1])'''

    # Get band data
#    red = get_band_data(dataset, file_param["band_order"]["B04"])
#    nir = get_band_data(dataset, file_param["band_order"]["B08"])

    # Calculate NDVI
    ndvi = (nir - red) / (nir + red)
    ndvi = set_no_data(ndvi, np.nan, 2)
    return ndvi


def calc_mintime(data):
    return np.fmin.reduce(data)


def calc_maxtime(data):
    return np.fmax.reduce(data)


if len(sys.argv) < 2:
    print("Data PID needs to be passed by command line argument.")
    sys.exit(-1)

data_pid = sys.argv[1]

# processing code
db = DatabaseSession(Base)

query = db.query(Query).filter_by(pid=data_pid).first()

if not query:
    print("Data PID  {} is not correct.".format(data_pid))
    sys.exit(-1)

