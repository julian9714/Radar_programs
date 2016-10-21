# -*- coing: utf-8 -*-
#!/usr/bin/env python
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Este modulo contiene clases para encontrar los datos coincidentes entre do series de tiempo
# Contine funciones par hacer ajustes entre los datos
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
import sys
sys.path.append('/home/julian/Dropbox/QPE/scripts/scripts_python/modulos_generales/')

import numpy as np
import useful_toolbox

class coincidentes(object):
    def __init__(self, fecha1, fecha2, serie1, serie2):
        self.fecha1 = fecha1
        self.fecha2 = fecha2
        self.serie1 = serie1
        self.serie2 = serie2
    def find_matches(self, return_coincidents = None):
        self.pos_same1 = np.in1d(self.fecha1, self.fecha2)
        self.pos_same2 = np.in1d(self.fecha2, self.fecha1)

        self.serie1_same = self.serie1[self.pos_same1 == True]
        self.fecha1_same = self.fecha1[self.pos_same1 == True]
        self.serie2_same = self.serie2[self.pos_same2 == True]
        if (return_coincidents is not None):
            self.dic_coinc = {'serie1_same' : self.serie1_same , 'serie2_same' : self.serie2_same,\
            'fecha_same':self.fecha1_same}
            return self.dic_coinc

def adjust_by_bins(N_bins, serie_x, serie_y):
    seriex_bins = np.copy(serie_x) 
    seriey_bins = np.copy(serie_y)

    seriex_bins[seriex_bins == 999.999] = np.nan
    seriex_bins[seriex_bins == -999.0] = np.nan
    seriex_bins[seriex_bins == -0.999] = np.nan

    seriey_bins[seriey_bins == 999.999] = np.nan
    seriey_bins[seriey_bins == -999.0] = np.nan
    seriey_bins[seriey_bins == -0.999] = np.nan
    
    mask_seriex = np.isnan(seriex_bins)
    max_value   = np.amax(seriex_bins[mask_seriex == False])
    min_value   = np.amin(seriex_bins[mask_seriex == False])
    size_step   = (max_value - min_value)/float(N_bins) 
    
    bound_min   = min_value - size_step/2.
    bound_max   = max_value + size_step/2.

    bin_array = np.array([bound_min])
    median_bin  = np.array([])
    mean_bin    = np.array([])
    mad_bin     = np.array([])
    q10_bin     = np.array([]) 
    q25_bin     = np.array([])
    q75_bin     = np.array([])
    q90_bin     = np.array([]) 

    bin_ini     = bound_min
    bin_fin     = bin_ini
    while (bin_fin <= bound_max):
        bin_fin   = bin_fin + size_step
        array_aux = seriey_bins[(seriex_bins >= bin_ini) & (seriex_bins < bin_fin)]
        
        if (len(array_aux) >= 15):
            quantils    = useful_toolbox.calculate_cuantiles([10, 25, 50, 75, 90], array_aux)
            dif_mad     = np.abs(array_aux - quantils[2])
            MAD         = (useful_toolbox.calculate_cuantiles([50], dif_mad))[0]
            elem_mean   = np.mean(array_aux[np.isnan(array_aux) == False])

            median_bin  = np.append(median_bin, quantils[2]) 
            mean_bin    = np.append(mean_bin, elem_mean) 
            mad_bin     = np.append(mad_bin, MAD) 
            q10_bin     = np.append(q10_bin, quantils[0])  
            q25_bin     = np.append(q25_bin, quantils[1]) 
            q75_bin     = np.append(q75_bin, quantils[3]) 
            q90_bin     = np.append(q90_bin, quantils[4])  
            
            bin_ini   = bin_fin
            bin_array = np.append(bin_array, bin_fin)         
        else:
            bin_fin   = bin_fin + size_step/2.    
  
    mean_point_arrayx = bin_array[0:-1] + (bin_array[1:] - bin_array[0:-1])/2.0 
    dict_res_bins  = {'bins': bin_array, 'mean_pointx':mean_point_arrayx, 'median':median_bin, 'q10':q10_bin,\
                    'q25':q25_bin, 'q75':q75_bin, 'q90':q90_bin, 'mad':mad_bin, 'mean':mean_bin} 

    return dict_res_bins

  
