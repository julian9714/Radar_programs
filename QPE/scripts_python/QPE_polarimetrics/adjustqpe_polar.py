# -*- coding: utf-8 -*-
import sys
sys.path.append('/home/julian/Dropbox/Radar_programs/QPE/scripts_python/modulos_generales/')
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

path_pkldata         = '/home/julian/Radar/QPE_pkl/'
str_pol              = '201'
str_est              = '201'
str_disdro           = '77'
res_ini              = '5MIN'
pklfile_polarimetric = str_pol+'_polarimetric.pkl'
pklfile_estacion     = str_est+'_precipitation.pkl'
pklfile_disdro       = str_disdro+'_disdrometro.pkl'
write_pklajust       = 'YES'
grap_pptvspolar      = 'NO'
grap_exppolar        = 'YES'

polar_data     = open_pklfiles(path_pkldata = path_pkldata+pklfile_polarimetric)
est_data       = open_pklfiles(path_pkldata = path_pkldata+pklfile_estacion)
disdro_data    = open_pklfiles(path_pkldata = path_pkldata+pklfile_disdro)

# Buscamos que las fechas en las que existen coincidentes segun la resolucion del radar
result_aux     = polar_data.join(disdro_data, how = 'inner')
coincidentes   = result_aux.join(est_data, how = 'inner')

julian
