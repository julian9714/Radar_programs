# Version 2 de read_netcdf.py
# En esta version lo que se hace es mejorar el codigo para que sea mas limpio

import numpy as np
import matplotlib as plt
import glob
import os 
import netCDF4

#path_file = '/home/julian/Dropbox/netcdf_radar/20130413/SAN-20130413-032132-PPIVol-01.nc.gz'
##path_file = '/home/julian/Dropbox/netcdf_radar/tmp_nc/SAN-20130413-032132-PPIVol-01.nc'
#path_out = '/home/julian/Dropbox/netcdf_radar/'
#aux_folder = 'tmp_nc'
#range_bound = 120.0
#elev_bound = 1.0

#################################################################################################
#################################################################################################

def unzip_nc (path_file, path_out, aux_folder):
    
    pos_gz = str.find(path_file, 'gz')
    try:
        os.system('mkdir '+path_out+aux_folder)
    except:
        pass
        #print 'El folder '+path_out+aux_folder+' ya existe'

    if pos_gz != -1:
        os.system('cp '+path_file+' '+path_out+aux_folder+'/')
        file_tmp = sorted(glob.glob(path_out+aux_folder+'/*.gz'))    
        os.system('gzip -dv '+file_tmp[0])
        file_nc = (sorted(glob.glob(path_out+aux_folder+'/*.nc')))[0]
        path_final = file_nc
    else:
        path_final = path_file
    
    return path_final

def clean_nc(path_final, aux_folder):
    pos_aux_folder = str.find(path_final, aux_folder)
    if pos_aux_folder != -1:
        print path_final
        os.system('rm -rf '+path_final)

def distance_to_deg (delta_x, delta_y, r_earth):
    d_lat = (delta_y/(r_earth)) 
    d_lon = delta_x /(r_earth * np.cos(d_lat*np.pi/180.))
    return {'delta_lon': d_lon*180.0/np.pi, 'delta_lat': d_lat*180./np.pi}


class variables_nc(object):
    'Se debe definir para la clase los siguientes parametros: \
    -- Ruta completa del archivo netcdf \
    -- Angulo de elevacion del barrido (elev_bound) \
    -- Rango maximo del barrido (range_bound)\
    El metodo getvariables_nc recibe una arreglo que puede contener \
    ALL --> Para leer todas las variables o se le puede sespecicicar que variable\
    se va leer (DBZH,DBZV,ZDR,RHOHV,PHIDP,NCPH,NCPV,SNRH,SNRV,VELH,VELV,WIDTHH,WIDTHV)'

    def __init__(self, folder_nc, elev_bound, range_bound):
        self.folder_nc = folder_nc
        self.elev_bound = int(np.floor(elev_bound*10.0))
        self.range_bound = int(range_bound)

    def print_att (self, display_att = 'NO'):
        f = netCDF4.Dataset(self.folder_nc, 'r')
        self.val_elevacion = int(np.round(np.amax(f.variables['elevation'][:]) * 10.))
        self.val_rango = int(np.ceil((np.amax(f.variables['range'][:]))/1000.0))
        f.close()
        
    def getvariables_nc(self, key_variables):
        self.key_variables = key_variables

        if ( self.val_rango == self.range_bound) & (self.val_elevacion ==  self.elev_bound):
            print 'Entre al condicional'
            print self.folder_nc
            nc = netCDF4.Dataset(self.folder_nc, 'r')
            self.name_varnc = np.array(['latitude','longitude','altitude',\
                'azimuth','elevation','range','sweep_number','sweep_mode',\
                    'fixed_angle','sweep_start_ray_index','sweep_end_ray_index'])
        
            if key_variables[0] == 'ALL':
                self.name_varnc = np.array([])
                for ij in nc.variables:
                    self.name_varnc = np.append(self.name_varnc, ij)
            else:
                self.name_varnc = np.append(self.name_varnc, key_variables)
            
            self.resul_nedcdf = {} 
            for ii in self.name_varnc:
                print 'La variable en el netcdf es :', ii
                try:
                    self.read_propname = nc.variables[ii]
                    self.resul_nedcdf.update({ii: {}})
                    self.values_nc = self.read_propname[:]
                    for jj in self.read_propname.__dict__:
                        self.attprop = self.read_propname.__dict__[jj]
                        self.resul_nedcdf[ii].update({jj:self.attprop})
                    try:
                        #self.values_nc[self.values_nc == self.read_propname._FillValue] = -999.0
                        #self.values_nc = (self.values_nc + 32.0)*2.
                        #self.values_nc[self.values_nc < 0.] =\
                        #        self.values_nc[self.values_nc < 0.] + 256.
                        #self.values_nc[np.isnan(self.values_nc) == False] =\
                        #        (self.values_nc[np.isnan(self.values_nc) == False]*\
                        #         self.read_propname.scale_factor) + self.read_propname.add_offset
                        print 'Se hizo el calculo de la matrix para '+ii
                        self.resul_nedcdf[ii].update({'Values': self.values_nc})
                        print 'Se hizo el calculo de la matrix el test '+ii
           
                    except:
                        print 'No se le modifica la variables con sacale y offset'
                        self.resul_nedcdf[ii].update({'Values': self.values_nc})
                except:
                    print 'La variable '+ii+'no se puede leer del netcdf'
            nc.close()                                                   
            return self.resul_nedcdf                                     
        else:                                                            
            print 'El rango y la elevacion no son las especificadas'     
                                                                         
print 'Compile bien'                                                     
                                                                         
##path_final = unzip_nc(path_file, path_out, aux_folder)                 
##test_class = variables_nc(path_final,elev_bound, range_bound)          
##jola = test_class.getvariables_nc(['DBZH'])                            
###clean_nc(path_final, aux_folder)                                      
#
#    
