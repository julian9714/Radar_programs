 # -*- coding: utf-8 -*-

import numpy as np
import math

def distance_to_deg (delta_x, delta_y, r_earth):
    d_lat = (delta_y/(r_earth)) 
    d_lon = delta_x /(r_earth * np.cos(d_lat*np.pi/180.))
    return {'delta_lon': d_lon*180.0/np.pi, 'delta_lat': d_lat*180./np.pi}

def deg_to_distance (latini, latfin, lonini, lonfin, r_earth):
    d_lat = np.array(latini - latfin)
    d_lon = np.array(lonfin - lonini)
    delta_y = (d_lat*np.pi/180.)*r_earth
    delta_x = (d_lon*np.pi/180.)*(r_earth * np.cos(d_lat*np.pi/180.))
    distance = ((delta_x**2.0) + (delta_y**2.0))**(1/2.0)
    return {'dist_m':distance, 'dist_km':distance/1000.}

def compute_heightradar(lat_radar, lon_radar, hr, lat_array, lon_array, elev):
    # this function retunr the height of a set points in comparison 
    # with the radar location (height in km)
    lat_rad = lat_radar*(math.pi/180.0)
    lon_rad = lon_radar*(math.pi/180.0)
    semi_eje_menor = 6356752.314
    semi_eje_mayor = 6378137.000
    radio = 1/(math.sqrt((math.cos(lat_rad)**2.0)/(semi_eje_mayor**2.0)+\
            (math.sin(lat_rad)**2.0)/(semi_eje_menor**2.0)))
    ra_e = (4./3.)*radio

    dist = deg_to_distance(lat_radar, lat, lon_radar, lon, radio)
    h = ((ra_e + hr)**2.0 + dist['dist_m']**2.0 + (2.*(ra_e + hr)*\
        dist['dist_m']*np.sin(ang*np.pi/180.0)))**(1./2.) - ra_e
    return h/1000.

lat_radar = 6.19329977036
lon_radar = -75.5271987915
hr = 2813.0
lat = np.array([6.85, 5.9, 6.95]) 
lon = np.array([-75.0, -75.8, -74.9])
ang = 1.0
heights = compute_heightradar(lat_radar, lon_radar, hr, lat, lon, elev=ang)
