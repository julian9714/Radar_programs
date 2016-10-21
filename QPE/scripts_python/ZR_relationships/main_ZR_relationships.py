# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -----------------------------------------------------
# Esto es una prueba
# Import necessary packages

import numpy as np
import ZR_relationships as ZR
import matplotlib.pyplot as plt
    
path_pkldata     = '/home/julian/Dropbox/Tesis/series_procesadas/desde_BD/'
name_stfiles     = 'estaciones_pkl_todaspaper.csv'
path_stations    = '/home/julian/Dropbox/Tesis/meta_informacion/'
path_plots       = '/home/julian/Dropbox/QPE/resultados/resultados_zr/'
source_str       = 'SIATA_Vaisala'
how_resolution   = 'Rolling'
type_fig_str     = 'Contour'
main_name_plot   = 'Contour'

resolution_array  = np.array(['Original', '15','30', '60', '90', '120','180'])
#resolution_array  = np.array(['15'])

box_arrayAorig = []
box_arrayBorig = []
box_arrayAbins = []
box_arrayBbins = []

for res in resolution_array:
    objet_test = ZR.zr_relation(path_pkldata = path_pkldata, name_stfiles = name_stfiles,\
        path_stations = path_stations)
    objet_test.finder_station(source = source_str)
    dict_all_data   =  objet_test.get_all(file_ext          = '.pkl', resolution = res, how_res = how_resolution,\
                                          type_figure       = 'Scatter',\
                                          path_plot         = path_plots,\
                                          name_plot_final   = main_name_plot)
    
    ppt_all_by_res = dict_all_data['ppt_all']
    ze_all_by_res  = dict_all_data['Ze_all']
    
    dict_obj       = {'ze_matches':ze_all_by_res, 'ppt_matches':ppt_all_by_res} 
    obj_zr_by_res  = ZR.plotter_zr(path_st = None, name_st = None, source = None)
    obj_zr_by_res.make_adjust(dict_obj)
    dic_corr_coef       = obj_zr_by_res.return_corr_coefficients()
    dict_coefficients   = obj_zr_by_res.return_adjust_coefficients()
    obj_zr_by_res.plot_ZR(type_plot = type_fig_str, path_plot = path_plots,\
                             name_plot_final = main_name_plot+'all_data',\
                             name_id = res+'_min', name_source = source_str)
    
    box_arrayAorig.append(dict_all_data['Aorig_all'])
    box_arrayBorig.append(dict_all_data['Borig_all'])
    box_arrayAbins.append(dict_all_data['Abin_all'])
    box_arrayBbins.append(dict_all_data['Bbin_all'])

# plot histogram adjust coeffiecients
plt.close()
plt.cla()
plt.clf() 

label_size = 9
fig1 = plt.figure(1)
fig1.set_figheight(6.4)
fig1.set_figwidth(4.0)
plt.subplots_adjust(left = 0.15,right = 0.95,top = 0.95, bottom = 0.1, hspace = 0.25, wspace = 0.25)

ax1 = fig1.add_subplot(211)
ax1.set_ylim(0, 500.0)
ax1.tick_params(axis='x', labelsize=label_size)
ax1.tick_params(axis='y', labelsize=label_size)
ax1.set_xlabel(u'Resolution [min]', fontsize = label_size)
ax1.set_ylabel(u'A values', fontsize = label_size)
box_1 = ax1.boxplot(box_arrayAorig, patch_artist = True ,showfliers = False)

for box in box_1['boxes']:
    box.set(color='k', linewidth=1.2)
    box.set(facecolor = '#123123')
for whisker in box_1['whiskers']:
    whisker.set(color='k', linewidth=1.2)

for cap in box_1['caps']:
    cap.set(color='k', linewidth=1.2)

for median in box_1['medians']:
    median.set(color='r', linewidth=1.6)

ax1.set_xticklabels(resolution_array)
#for flier in box_1['fliers']:
#    flier.set(marker='o', color='#e7298a', alpha=0.5)


ax2 = fig1.add_subplot(212)
ax2.set_ylim(0., 4.0)
ax2.tick_params(axis='x', labelsize=label_size)
ax2.tick_params(axis='y', labelsize=label_size)
ax2.set_xlabel(u'Resolution [min]', fontsize = label_size)
ax2.set_ylabel(u'B values', fontsize = label_size)
box_2 = ax2.boxplot(box_arrayBorig, showfliers = False)

for box in box_2['boxes']:
    box.set(color='k', linewidth=1.2)

for whisker in box_2['whiskers']:
    whisker.set(color='k', linewidth=1.2)

for cap in box_2['caps']:
    cap.set(color='k', linewidth=1.2)

for median in box_2['medians']:
    median.set(color='r', linewidth=1.6)

ax2.set_xticklabels(resolution_array)

plt.savefig('/home/julian/Dropbox/QPE/resultados/resultados_zr/box_coef_orig_'+source_str+'.png',\
    format = 'png', dpi = 300)


plt.close()
plt.cla()
plt.clf() 

label_size = 9
fig1 = plt.figure(1)
fig1.set_figheight(6.4)
fig1.set_figwidth(4.0)
plt.subplots_adjust(left = 0.15,right = 0.95,top = 0.95, bottom = 0.1, hspace = 0.25, wspace = 0.25)

ax1 = fig1.add_subplot(211)
ax1.set_ylim(0., 500.)
ax1.tick_params(axis='x', labelsize=label_size)
ax1.tick_params(axis='y', labelsize=label_size)
ax1.set_xlabel(u'Resolution [min]', fontsize = label_size)
ax1.set_ylabel(u'A values', fontsize = label_size)
box_1 = ax1.boxplot(box_arrayAbins, showfliers = False)

for box in box_1['boxes']:
    box.set(color='k', linewidth=1.2)

for whisker in box_1['whiskers']:
    whisker.set(color='k', linewidth=1.2)

for cap in box_1['caps']:
    cap.set(color='k', linewidth=1.2)

for median in box_1['medians']:
    median.set(color='r', linewidth=1.6)

ax1.set_xticklabels(resolution_array)
#for flier in box_1['fliers']:
#    flier.set(marker='o', color='#e7298a', alpha=0.5)


ax2 = fig1.add_subplot(212)
ax2.set_ylim(0., 4.0)
ax2.tick_params(axis='x', labelsize=label_size)
ax2.tick_params(axis='y', labelsize=label_size)
ax2.set_xlabel(u'Resolution [min]', fontsize = label_size)
ax2.set_ylabel(u'B values', fontsize = label_size)
box_2 = ax2.boxplot(box_arrayBbins, showfliers = False)

for box in box_2['boxes']:
    box.set(color='k', linewidth=1.2)

for whisker in box_2['whiskers']:
    whisker.set(color='k', linewidth=1.2)

for cap in box_2['caps']:
    cap.set(color='k', linewidth=1.2)

for median in box_2['medians']:
    median.set(color='r', linewidth=1.6)

ax2.set_xticklabels(resolution_array)

plt.savefig('/home/julian/Dropbox/QPE/resultados/resultados_zr/box_coef_bins_'+source_str+'.png',\
    format = 'png', dpi = 300)







