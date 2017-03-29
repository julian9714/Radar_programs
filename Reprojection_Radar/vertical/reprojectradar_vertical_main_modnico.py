# -*- coding: utf-8 -*-
import useful_toolbox as mytools
import read_parsingfile as r_pf
import read_ncdatav2 as r_nc
import glob
import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from scipy.interpolate import griddata
import datetime as dt
import numpy as np

# Definicion de la ruta del archivo de las variables de entrada
path_prop = '/mnt/external_hdd/Radar_programs/Reprojection_Radar/vertical/'
path_data = '/mnt/external_hdd/nc_data/RHI/20130627/'
path_topo = '/mnt/external_hdd/Radar_programs/Reprojection_Radar/vertical/'
file_properties = 'reprojectradar_properties.ini'

dic_inprop = r_pf.parsing_file(path_prop, file_properties).get_parsingpar()

list_filesnc = np.array(sorted(glob.glob(path_data+'*RHIVol*.nc')))
#list_filesnc = np.array(['/mnt/external_hdd/nc_data/RHI/20140426/SAN-20140426-034120-RHIVol-01.nc'])
#list_filesnc = np.array(['/home/julian/Radar/datos/20130627/SAN-20130627-114130-RHIVol.nc'])
#list_filesnc = np.array(['/home/julian/Desktop/nc/SAN-20150529-192049-RHIVol-001.nc'])


# Se obtienen las variables del nc como una array a paritr del alrchivo parseado.
str_namenc = np.array(['DBZH'])

#--------------------------------------------------------------------------------------------------
# lectura de los puntos para la topografia
#--------------------------------------------------------------------------------------------------
data_topo = np.fromfile(path_topo+'TopoZonal.dat', sep = '    ', dtype = float)
n_topo    = data_topo[0]
lon_topo  = (data_topo[1:])[0:n_topo]
lon_fix   = (data_topo[1:])[n_topo:]
#---------------------------------------------------------------------------------------------------
# Definimos las varibales para hacer la reproyeccion.
# Definicion del semi eje menor y el semi eje menor deacuerdo al wgs84
semi_eje_menor = 6356752.314
semi_eje_mayor = 6378137.000
#----------------------------------------------------------------------------------------------------
for ii in list_filesnc:
    print ii
    str_dateUTC   = (((ii.split('SAN-'))[1]).split('-RHIVol'))[0]
    datelocal     = (dt.datetime.strptime(str_dateUTC, '%Y%m%d-%H%M%S')) - dt.timedelta(hours = 5)
    str_datelocal = dt.datetime.strftime(datelocal, '%Y%m%d-%H%M%S')

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
    range_s = dic_varnc['range']['Values']
    azimuth = dic_varnc['azimuth']['Values']
    elev    = (dic_varnc['elevation']['Values'])*(np.pi/180.)
    fixed_angles = np.round((dic_varnc['fixed_angle']['Values'])[0])
    print 'El maximo de los datos es: ', np.amax(dic_varnc['DBZH']['Values'])

    h_all    = np.array([])
    s_all    = np.array([])
    var_all  = np.array([])

    for jj in range(len(elev)):
        h = ((ra_e + hr)**2.0 + range_s**2.0 + (2.*(ra_e + hr)*range_s*np.sin(elev[jj])))**\
              (1./2.) - ra_e
        s = ra_e * np.arcsin((range_s/(h + ra_e)) * np.cos(elev[jj]))
        aux_var = (dic_varnc['DBZH']['Values'])[jj, :]
        h_all   = np.append(h_all, h)
        s_all   = np.append(s_all, s)
        var_all = np.append(var_all, aux_var)

    # Convertimos los parametros de la reproyeccion en metros 
    h_km     = np.copy(h_all)/1000.
    s_km     = np.copy(s_all)/1000.
    grid_alt = np.linspace(0, 18., 120.)
    grid_hoz = np.linspace(0, 119., 650.)

    # LLevamos los datos de la reproyeccion a una malla regular
    X, Y     = np.meshgrid(grid_hoz, grid_alt)
    point    = np.transpose(np.array([s_km, h_km]))
    grid_z0  = griddata(point, var_all, (X, Y), method='nearest')
    print 'El maximo del reproyectado es: ', np.nanmax(grid_z0)

    angles   = np.array([0.0, 1.0, 10.0, 40.0])
    rep_dict = {}
    for ang in angles:
        h = ((ra_e + hr)**2.0 + range_s**2.0 + (2.*(ra_e + hr)*range_s*np.sin(ang*np.pi/180.0)))**\
              (1./2.) - ra_e
        s = ra_e * np.arcsin((range_s/(h + ra_e)) * np.cos(ang*np.pi/180.))
        rep_dict.update({'ang'+np.str(ang):{'h':h/1000., 's': s/1000.}})

    # Hacemos una mascara donde no existen datos arriaba de los 40 grados y debajo de 0
    bounds_d  = rep_dict['ang0.0']['s']
    bounds_u  = rep_dict['ang40.0']['s']
    boundh_d  = rep_dict['ang0.0']['h']
    boundh_u  = rep_dict['ang40.0']['h']
    bhreal_d  = np.empty(len(grid_hoz), float)
    bhreal_u  = np.empty(len(grid_hoz), float)
    delta_hoz = (grid_hoz[1] - grid_hoz[0])/2.0
    mask_rhi = np.ones((len(grid_alt), len(grid_hoz)))
    for kk in range(len(grid_hoz)):
        pos_d = (np.where((bounds_d >= (grid_hoz[kk]-delta_hoz)) &\
                (bounds_d <= (grid_hoz[kk]+delta_hoz))))[0]
        h_d   = np.mean(boundh_d[pos_d])
        bhreal_d[kk] = h_d

        pos_u = (np.where((bounds_u >= (grid_hoz[kk]-delta_hoz)) &\
                (bounds_u <= (grid_hoz[kk]+delta_hoz))))[0]
        h_u   = np.mean(boundh_u[pos_u])
        bhreal_u[kk] = h_u
        aux_mask = mask_rhi[:, kk]
        aux_mask[(grid_alt <= h_d) | (grid_alt >= h_u)] = 0.0
        mask_rhi[:, kk] = aux_mask

    grid_z0[mask_rhi == 0.0] = np.nan
    var_rep_z0    = np.flipud(grid_z0) # Se hace el flip de la matrix
    test_m        = np.fliplr(grid_z0)
    delta_lon     = lon_fix - dic_varnc['longitude']['Values']
    topo_londist  = delta_lon*110.
    plot_topo_lon = (np.append(np.array([0]), (topo_londist[topo_londist <= 0])[::-1]))*-1.
    plot_topo_hg  = (np.append(np.array([dic_varnc['altitude']['Values']]), (lon_topo[topo_londist <= 0])[::-1]))/1000.

    aux = np.array([0, 20, 40, 60, 80, 100, 119])
    ax_deg = dic_varnc['longitude']['Values'] - aux/110.

    color   =  [(43, 110, 255), (0, 57, 200), (66, 197, 212), (7, 240, 8),\
                (11, 168, 29),\
                (0, 117, 12), (255, 248, 0), (242, 174, 46), (242, 188, 107),\
                (222 , 115, 0), (255, 0, 0),\
                (158, 29, 0), (255, 117, 255), (252, 201, 255)]
        
    my_colorbar = mytools.make_cmap(colors=color, bit=True)  
    lev = np.array([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 80])
    norm = colors.BoundaryNorm(boundaries=lev, ncolors=256)

    test_m[test_m < 0.0] = np.nan
    if ((dic_varnc['fixed_angle']['Values'])[0] == 270.):
        plt.close('ALL')
        plt.cla()
        plt.clf()
        fig1 = plt.figure(1)
        fig1.set_figheight(5.0)
        fig1.set_figwidth(5.0)
        plt.subplots_adjust(left=0.15,right=0.95,top=0.95,bottom=0.1,hspace=0.25,wspace=0.25)
        labelsize = 9
        ax1 = fig1.add_subplot(111)
        matplotlib.rcParams['axes.labelsize'] = labelsize
        ax1.tick_params(axis='x', labelsize=labelsize)
        ax1.tick_params(axis='y', labelsize=labelsize)
        ax1.set_xlabel('Longitud', fontsize = labelsize)
        ax1.set_ylabel('Altura $[km]$', fontsize = labelsize)
        ax1.set_xlim(60.0, 119.)
        ax1.set_ylim(0.0, 13.0)
        plt.xticks(aux[3:], (map(lambda x : str('%0.2f'%x),ax_deg[::-1]))[3:])
        img = ax1.imshow(test_m, aspect='auto', origin='lower', cmap = my_colorbar, norm = norm,\
                         extent=(X.min(), X.max(), Y.min(), Y.max()))
        ax1.plot(aux, np.array([2]*7), alpha = 0)
        ax1.plot(np.array([101]*28), np.arange(0.0, 14.0, 0.5), color = 'k', lw = 1.2, ls = '--')
        ax1.plot(rep_dict['ang0.0']['s'], (rep_dict['ang0.0']['h'])[::-1], lw = 1.0, c = 'k', ls = ':')
        ax1.plot(rep_dict['ang1.0']['s'], (rep_dict['ang1.0']['h'])[::-1], lw = 1.0, c = 'k', ls = ':')
        ax1.plot(rep_dict['ang10.0']['s'], (rep_dict['ang10.0']['h'])[::-1], lw = 1.0,\
                 c = 'k', ls = ':')
        ax1.plot((rep_dict['ang40.0']['s']) + 28., (rep_dict['ang40.0']['h'])[::-1], lw = 1.0,\
                 c = 'k', ls = ':')
        ax1.plot(plot_topo_lon-120, plot_topo_hg[::-1], color = 'k')
        ax1.fill_between(plot_topo_lon-120., plot_topo_hg[::-1], where=plot_topo_hg[::-1] >= 0,\
                         facecolor='gray', interpolate=True)
        cbar = plt.colorbar(img, fraction=0.1, pad=0.1, orientation = 'horizontal',\
                            label = 'Reflectividad $[dBZ]$')
        cbar.ax.tick_params(labelsize=labelsize)
        
        plt.savefig('/mnt/external_hdd/Radar_results/resultado_RHI/Reflectividad_'+str_datelocal+'_RHI_AZ'+str(int((dic_varnc['fixed_angle']['Values'])[0]))+'.png', format = 'png', dpi = 300)
