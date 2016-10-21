import numpy as np
import read_parsingfile as r_pf
import read_ncdatav2 as r_nc  
import glob
import math
import matplotlib.pyplot as plt
from scipy.interpolate import griddata 

# Definicion de la ruta del archivo de las variables de entrada
path_prop = '/home/julian/Dropbox/Tesis/tesis_progs/Reproyecta_radar/'
file_properties = 'reprojectradar_properties.ini'

dic_inprop = r_pf.parsing_file(path_prop, file_properties).get_parsingpar()

#list_filesnc = np.array(sorted(glob.glob(dic_inprop['path_file']+'*/*PPI*.nc*')))
#list_filesnc = np.append(list_filesnc,sorted(glob.glob(dic_inprop['path_file']+'*/*.nc')))

list_filesnc = np.array(['/home/julian/Documents/nc_data/SAN-20150529-233946-PPIVol-001.nc'])
# Se obtienen las variables dle nc como una array a paritr del alrchivo parseado.
str_namenc =np.array(str.split(dic_inprop['array_varnc'], ';'))

# ----------------------------------------------------------------------------------------------------------
# Definimos las varibales para hacer la reproyeccion.
# Definicion del semi eje menor y el semi eje menor deacuerdo al wgs84
semi_eje_menor = 6356752.314
semi_eje_mayor = 6378137.000

#-----------------------------------------------------------------------------------------------------------
for ii in list_filesnc:    
    path_data = r_nc.unzip_nc(ii, dic_inprop['path_out'], dic_inprop['aux_folder'])
    lee_varnc = r_nc.variables_nc(path_data,dic_inprop['elev_bound'], dic_inprop['range_bound'])
    lee_varnc.print_att() 
    dic_varnc = lee_varnc.getvariables_nc(str_namenc)
    r_nc.clean_nc(path_data, dic_inprop['aux_folder'])
        
    lat_rad = dic_varnc['latitude']['Values'] * (math.pi/180.0)
    lon_rad = dic_varnc['longitude']['Values'] * (math.pi/180.0)

    # radio de la tierra en la latitud del radar
    radio = 1/(math.sqrt((math.cos(lat_rad)**2.0)/(semi_eje_mayor**2.0)+\
            (math.sin(lat_rad)**2.0)/(semi_eje_menor**2.0)))
    ra_e = (4./3.)*radio
    hr   = dic_varnc['altitude']['Values']
    n_sweeps = len(dic_varnc['sweep_number']['Values'])
    range_s = dic_varnc['range']['Values']
    azimuth = dic_varnc['azimuth']['Values']
    elev    = np.round(np.amax(dic_varnc['elevation']['Values']))*(np.pi/180.)

    h = ((ra_e + hr)**2.0 + range_s**2.0 + (2.*(ra_e + hr)*range_s*np.sin(elev)))**\
          (1./2.) - ra_e
    s = ra_e * np.arcsin((range_s/(h + ra_e)) * np.cos(elev))
    
    cos_y = np.copy(azimuth)
    sen_x = np.copy(azimuth)

    cos_y[(azimuth>=0.0)&(azimuth<=90.)]=np.cos((azimuth[(azimuth>=0.0)&(azimuth<=90.)])*\
           np.pi/180.)
    cos_y[(azimuth>90.)&(azimuth<=180.)]=-np.cos((180. - azimuth[(azimuth>90.)&(azimuth<=180.)])*\
           np.pi/180.)
    cos_y[(azimuth>180.)&(azimuth<=270.)]=-np.cos((azimuth[(azimuth>180.)&(azimuth<=270.)]-180.)*\
           np.pi/180.)
    cos_y[(azimuth>270.)&(azimuth<=360.)]=np.cos((360. - azimuth[(azimuth>270.)&(azimuth<=360.)])*\
           np.pi/180.)
    
    sen_x[(azimuth>=0.0)&(azimuth<=90.)]=np.sin((azimuth[(azimuth>=0.0)&(azimuth<=90.)])*\
           np.pi/180.)
    sen_x[(azimuth>90.)&(azimuth<=180.)]=np.sin((180.-azimuth[(azimuth>90.)&(azimuth<=180.)])*\
           np.pi/180.)
    sen_x[(azimuth>180.)&(azimuth<=270.)]=-np.sin((azimuth[(azimuth>180.)&(azimuth<=270.)]-180.)*\
           np.pi/180.)
    sen_x[(azimuth>270.)&(azimuth<=360.)]=-np.sin((360.-azimuth[(azimuth>270.)&(azimuth<=360.)])*\
           np.pi/180.)

    delta_x    = np.array([])
    delta_y    = np.array([])
    var_array  = np.array([])
    var_array2 = np.array([])
    for kk in range(len(azimuth)):
        aux_dx    = sen_x[kk]*s
        aux_dy    = cos_y[kk]*s
        aux_varr  = (dic_varnc['DBZH']['Values'])[kk, :]
        aux_varr2  = (dic_varnc['VELH']['Values'])[kk, :]
        
        delta_x   = np.append(delta_x, aux_dx) 
        delta_y   = np.append(delta_y, aux_dy) 
        var_aa rray = np.append(var_array, aux_varr)
        var_array2 = np.append(var_array2, aux_varr2)
 
    lat=dic_varnc['latitude']['Values']+(r_nc.distance_to_deg(delta_x, delta_y, radio))['delta_lat']
    lon=dic_varnc['longitude']['Values']+(r_nc.distance_to_deg(delta_x, delta_y, radio))['delta_lon']

    ## Hacemos la interpolacion
    grid_lat = np.array([float(dic_inprop['minlat120'])]*500) + np.arange(0,500,1)*0.005#\
                         #float(dic_inprop['resx120'])
    grid_lon = np.array([float(dic_inprop['minlon120'])]*500) + np.arange(0,500,1)*0.005#\
                         #float(dic_inprop['resy120'])

    X, Y = np.meshgrid(grid_lon, grid_lat)
    point = np.transpose(np.array([lon, lat]))

    var_array[var_array == -32768.] = np.nan
    var_array2[var_array2 == -32768.] = np.nan
    grid_z0  = griddata(point, var_array, (X, Y), method='nearest')
    grid_vel = griddata(point, var_array2, (X, Y), method='nearest')

    var_rep_z0  = np.flipud(grid_z0) 
    var_rep_vel = np.flipud(grid_vel)

    plt.close('ALL')
    plt.cla()
    plt.clf()
    plt.imshow(var_rep_z0)
    #plt.scatter(grid_lon[np.isnan(var_array) == False], grid_lat[np.isnan(var_array) == False])
    plt.colorbar()
    plt.savefig('cosa.png', format = 'png', dpi = 300)
