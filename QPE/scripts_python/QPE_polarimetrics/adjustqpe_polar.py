# -*- coding: utf-8 -*-
import sys
sys.path.append('/home/julian/Radar_programs/QPE/scripts_python/modulos_generales/')
from useful_toolbox import *
import numpy as np
import datetime as dt 
import matplotlib
matplotlib.use('template')
import matplotlib.pyplot as plt
import os
import matplotlib.dates as md
import pprint, pickle
import pandas as pd
import glob
import modulos_qpepolares as qpepolar

path_pkldata     = '/mnt/external_hdd/Radar_data/QPE_pkl/'
name_stfiles     = 'estaciones_pkl_todaspaper.csv'
path_stations    = '/mnt/external_hdd/Radar_data/meta_informacion/'
path_plots       = '/home/julian/Dropbox/QPE/resultados/resultados_zr/'
source_str       = 'SIATA_Vaisala'
#how_resolution   = 'Rolling'
#type_fig_str     = 'Contour'
#main_name_plot   = 'Contour'

polar_data = qpepolar.polar_QPE(path_pkldata, name_stfiles, path_stations)
test       = polar_data.finder_station(source = source_str)
