# Este modulo contiene funcuones que grafican las series
# Grafica sccater plots --- Busca los coincidentes.
# Hace ajustes Lineales y con varias variables.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
import read_seriesdb as rdb
import scatters_series as scs
import calculate_matches as cal_matches
import modulo_ajustemulticapa as ajustmc

def make_pickle(path_out, name_pkl, df_pkl):
    output_file = open(path_out+name_pkl+'.pkl', 'wb')
    pickle.dump(df_pkl, output_file)
    output_file.close()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Parametros de entrada
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Parametros de ajuste y graficAS 
path_pkldata = '/home/julian/Dropbox/Tesis/series_procesadas/desde_BD/'
fecha_inicial = '2014-10-15 00:00'
fecha_final = '2015-10-31 23:59'

## Modificacion SAMANA
#path_pkldata = '/home/julian/Dropbox/SIATA/Isagen/QPE_Isagen/datos_procesados/'
#fecha_inicial = '2015-10-10 00:00'
#fecha_final = '2015-10-31 23:59'
# ------------------------

##fecha_inicial = '2015-03-20 00:00'
#fecha_final = '2015-03-22 04:00'
estacion = '160'
est_aux = '160'
str_disdro = '159'
grafica_scatters = 'YES'
#path_plotout = '/home/julian/Dropbox/Tesis/Resultados/Graficas_finales/Ajuste_disdrometro/'
path_plotout = '/home/julian/Desktop/'
#path_writepkl_multicapas = '/home/julian/Dropbox/Tesis/meta_informacion/coeficientes_ajuste/'

### Modificacion
path_writepkl_multicapas = '/home/julian/Desktop/'
# -----------------------------------
write_pklajust = 'YES'

# Parametros consulta
consultar_BD = 'NO' # Si la 
str_elev = '1'
source_dis = 'Disdrometro'
if len(estacion) == int(7): source_str = 'EPM'
if len(estacion) == int(3): source_str = 'SIATA_Vaisala'
if len(estacion) <= int(2): source_str = 'SIATA'

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# definicion de fechas pra eventos preclasificados 
tabla_eventos = np.genfromtxt('/home/julian/Dropbox/Tesis/meta_informacion/resumen_eventos.csv', delimiter = ';', dtype = np.str)
str_fecha = np.array(map(lambda x,y:  str.strip(x + y), tabla_eventos[1:,1], tabla_eventos[1:,2]))
duracion_min = np.array(map(int, tabla_eventos[1:, 4]))
tipo_str =np.array(map(lambda x: str.strip(x), tabla_eventos[1:, 5]))

fecha_inicial_file = map(lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M') + dt.timedelta(minutes = -30), str_fecha)
fecha_final_file = map(lambda x,y: dt.datetime.strptime(x, '%Y-%m-%d %H:%M') + dt.timedelta(minutes = +y + 30), str_fecha, duracion_min)
fini_str = np.array(map(lambda x :dt.datetime.strftime(x, '%Y-%m-%d %H:%M'), fecha_inicial_file))
ffin_str = np.array(map(lambda x :dt.datetime.strftime(x, '%Y-%m-%d %H:%M'), fecha_final_file))
##Definicion manual de fechas
#fini_str =np.array(['2015-03-21 00:00'])
#ffin_str =np.array(['2015-03-21 04:00'])
#tipo_str = np.array(['convectivo'])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Consyltas en base de datos 
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
if consultar_BD == 'YES':
    psql_pol = rdb.consulta_psql(str_elev)
    psql_pol.make_query(fecha_inicial, fecha_final, estacion)
    polar_data = psql_pol.get_variables()

    mysql_ppt = rdb.consulta_mysql(source_str)
    mysql_ppt.make_query(fecha_inicial, fecha_final, estacion)
    est_data = mysql_ppt.get_variables()

    mysql_disdro = rdb.consulta_mysql(source_dis)
    mysql_disdro.make_query(fecha_inicial, fecha_final, str_disdro)
    disdro_data = mysql_disdro.get_variables()
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Lectura de los archivos dado que no se realiza la consulta en la base de datos 
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
if consultar_BD == 'NO':
    path_estpol = sorted(glob.glob(path_pkldata+est_aux+'_polarimetric.pkl'))
    pkl_estpol = open(path_estpol[0], 'rb')
    polar_data = pickle.load(pkl_estpol)
    pkl_estpol.close()
    # Leo precipitacion de la estacion 
    path_estppt = sorted(glob.glob(path_pkldata+estacion+'_precipitation.pkl'))
    pkl_estppt = open(path_estppt[0], 'rb')
    est_data = pickle.load(pkl_estppt)
    pkl_estppt.close()
    # Leo datos del disdrometro
    path_estdisdro = sorted(glob.glob(path_pkldata+str_disdro+'_disdrometro.pkl'))
    pkl_estdisdro = open(path_estdisdro[0], 'rb')
    disdro_data = pickle.load(pkl_estdisdro)
    pkl_estdisdro.close()
    
    # Se indexan los data frame extraidos del pkl segun la fecha inicial y final que se pongan
    polar_data = polar_data[fecha_inicial:fecha_final]
    est_data = est_data[fecha_inicial:fecha_final]
    disdro_data = disdro_data[fecha_inicial:fecha_final]
    
date_pols = polar_data.index
dbzh_s = polar_data.dbzh.values
dbzv_s = polar_data.dbzv.values
zdr_s = polar_data.zdr.values
phidp_s = polar_data.phidp.values
rhohv_s = polar_data.rhohv.values
rhohv_s[rhohv_s >= 1000.0] = rhohv_s[rhohv_s >= 1000.0]*0.0001

fecha_est = est_data.index
ppt_rate = (est_data.ppt_int.values)

fecha_disdro = disdro_data.index
ref_disdro = disdro_data.Ref_disdro.values
pptrate_disdro = (disdro_data.ppt_all.values)

N_bins = 20
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Calculo de fechas dond existen coincidentes y ajuste usando le modulo calculate_matches.py
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
dict_coef = ajustmc.calculate_coef (N_bins = N_bins, fecha_disdro = fecha_disdro ,date_pols = date_pols,fecha_est = fecha_est,ref_disdro = ref_disdro,\
    dbzh_s = dbzh_s, dbzv_s = dbzv_s, pptrate_disdro = pptrate_disdro, ppt_rate = ppt_rate, ajust_qq = 'NO',str_disdro= str_disdro,estacion=estacion, grafica_scatters = 'YES', path_plotout = path_plotout, pass_by_zero = 'NO', write_clases = 'SI')
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fragmento de cogigo donde se realizan las estimaciones por Eventos
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
dict_outall = ajustmc.ajuste_multicapa(dict_coef = dict_coef, polar_data = polar_data, est_data = est_data ,disdro_data = disdro_data, fini_str = fini_str, ffin_str = ffin_str,\
    tipo_str = tipo_str,res_resample = '5Min', width_smooth = 0, make_grafica = 'NO' ,trunc = 50)

Ajustall_convectivos = dict_outall['convectivo']['Ppt_ajust']
observado_convectivos = dict_outall['convectivo']['Ppt_observada']
fini_convectivos = dict_outall['convectivo']['fini']
ffin_convectivos = dict_outall['convectivo']['ffin']

Ajustall_estratiformes = dict_outall['estratiforme']['Ppt_ajust']
observado_estratiformes = dict_outall['estratiforme']['Ppt_observada']
fini_estratiformes = dict_outall['estratiforme']['fini']
ffin_estratiformes = dict_outall['estratiforme']['ffin']

Ajustall_mixed = dict_outall['mixed']['Ppt_ajust']
observado_mixed = dict_outall['mixed']['Ppt_observada']
fini_mixed = dict_outall['mixed']['fini']
ffin_mixed = dict_outall['mixed']['ffin']
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Ajustes por tipo de evento
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
polardata_convectivo = pd.DataFrame()
estdata_convectivo = pd.DataFrame()
disdrodata_convectivo = pd.DataFrame()

for fi_cc, ff_cc in zip(fini_convectivos, ffin_convectivos):
    polardata_convectivo = polardata_convectivo.append(polar_data[fi_cc:ff_cc])
    estdata_convectivo = estdata_convectivo.append(est_data[fi_cc:ff_cc])
    disdrodata_convectivo = disdrodata_convectivo.append(disdro_data[fi_cc:ff_cc])
    
dict_coef_conv = ajustmc.calculate_coef (N_bins = N_bins, fecha_disdro =  disdrodata_convectivo.index ,date_pols = polardata_convectivo.index,fecha_est = estdata_convectivo.index,ref_disdro = disdrodata_convectivo.Ref_disdro.values,\
    dbzh_s = polardata_convectivo.dbzh.values, dbzv_s = polardata_convectivo.dbzv.values, pptrate_disdro = disdrodata_convectivo.ppt_all.values, ppt_rate = estdata_convectivo.ppt_int.values,\
        ajust_qq = 'YES', str_disdro= str_disdro,estacion=estacion, grafica_scatters = 'NO', path_plotout = path_plotout, pass_by_zero = 'YES')    

dict_outconv = ajustmc.ajuste_multicapa(dict_coef = dict_coef_conv, polar_data = polar_data, est_data = est_data ,disdro_data = disdro_data, fini_str = fini_str, ffin_str = ffin_str,\
    tipo_str = tipo_str,res_resample = '5Min', width_smooth = 0, make_grafica = 'NO' ,trunc = 50.0)

polardata_estratiforme = pd.DataFrame()
estdata_estratiforme = pd.DataFrame()
disdrodata_estratiforme = pd.DataFrame()

for fi_ee, ff_ee in zip(fini_estratiformes, ffin_estratiformes):
    polardata_estratiforme = polardata_estratiforme.append(polar_data[fi_ee:ff_ee])
    estdata_estratiforme = estdata_estratiforme.append(est_data[fi_ee:ff_ee])
    disdrodata_estratiforme = disdrodata_estratiforme.append(disdro_data[fi_ee:ff_ee])
    
dict_coef_est = ajustmc.calculate_coef (N_bins = N_bins, fecha_disdro =  disdrodata_estratiforme.index ,date_pols = polardata_estratiforme.index,fecha_est = estdata_estratiforme.index,ref_disdro = disdrodata_estratiforme.Ref_disdro.values,\
    dbzh_s = polardata_estratiforme.dbzh.values, dbzv_s = polardata_estratiforme.dbzv.values, pptrate_disdro = disdrodata_estratiforme.ppt_all.values, ppt_rate = estdata_estratiforme.ppt_int.values,\
        ajust_qq = 'YES', str_disdro= str_disdro,estacion=estacion, grafica_scatters = 'NO', path_plotout = path_plotout, pass_by_zero = 'YES')    

dict_outest = ajustmc.ajuste_multicapa(dict_coef = dict_coef_est, polar_data = polar_data, est_data = est_data ,disdro_data = disdro_data, fini_str = fini_str, ffin_str = ffin_str,\
    tipo_str = tipo_str,res_resample = '5Min', width_smooth = 0, make_grafica = 'NO' ,trunc = 50.0)

polardata_mixed = pd.DataFrame()
estdata_mixed = pd.DataFrame()
disdrodata_mixed = pd.DataFrame()

for fi_mm, ff_mm in zip(fini_mixed, ffin_mixed):
    polardata_mixed = polardata_mixed.append(polar_data[fi_mm:ff_mm])
    estdata_mixed = estdata_mixed.append(est_data[fi_mm:ff_mm])
    disdrodata_mixed = disdrodata_mixed.append(disdro_data[fi_mm:ff_mm])

dict_coef_mix = ajustmc.calculate_coef (N_bins = N_bins, fecha_disdro =  disdrodata_mixed.index ,date_pols = polardata_mixed.index,fecha_est = estdata_mixed.index,ref_disdro = disdrodata_mixed.Ref_disdro.values,\
    dbzh_s = polardata_mixed.dbzh.values, dbzv_s = polardata_mixed.dbzv.values, pptrate_disdro = disdrodata_mixed.ppt_all.values, ppt_rate = estdata_mixed.ppt_int.values,\
        ajust_qq = 'YES', str_disdro= str_disdro,estacion=estacion, grafica_scatters = 'NO', path_plotout = path_plotout, pass_by_zero = 'YES')    

dict_outmix = ajustmc.ajuste_multicapa(dict_coef = dict_coef_mix, polar_data = polar_data, est_data = est_data ,disdro_data = disdro_data, fini_str = fini_str, ffin_str = ffin_str,\
    tipo_str = tipo_str,res_resample = '5Min', width_smooth = 0, make_grafica = 'NO' ,trunc = 50.0)

## Se escriben los archivos pkl 
## con los diccionarios de los ajustes de las diferentes capas
make_pickle(path_writepkl_multicapas, 'ajuste_multicapaall_'+str_disdro, dict_coef)
make_pickle(path_writepkl_multicapas, 'ajuste_multicapaconvectivo_'+str_disdro, dict_coef_conv)
make_pickle(path_writepkl_multicapas, 'ajuste_multicapaestratiforme_'+str_disdro, dict_coef_est)
make_pickle(path_writepkl_multicapas, 'ajuste_multicapamixed_'+str_disdro, dict_coef_mix)

size_font = 16 
plt.close('all')
plt.cla()
plt.clf()

fig6 = plt.figure(6,figsize=(20, 15))
plt.subplots_adjust(left = 0.05,right = 0.95,top = 0.95, bottom = 0.2 ,hspace = 0.35, wspace = 0.1)
vax = fig6.add_subplot(2,2,1)
my_xticks = map(lambda x: x[0:10],fini_convectivos)
vax.set_xlim(-1, len(fini_convectivos)+1)
vax.set_ylim(0, 90)
#plt.yscale('symlog')
vax.set_title('Precipitacion Acumulada - Eventos Convectivos', fontsize = 18)
vax.set_xlabel('Fecha ocurrencia eventos', fontsize = size_font)
vax.set_ylabel('Precipitacion Acumulada (mm)', fontsize = size_font)
vax.tick_params(axis='x', labelsize= size_font)
vax.tick_params(axis='y', labelsize= size_font)
plt.xticks(np.arange(0,len(fini_convectivos),1) + 0.5, my_xticks, rotation=330)
vax.plot(np.arange(0,len(fini_convectivos),1), Ajustall_convectivos, color = 'k', label = 'Preciptacion Ajustada con todos los eventos', marker = '*', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_convectivos),1), observado_convectivos, color = 'b', linewidth = 0.8, label = 'Precipitaion Observada', marker = 's', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_convectivos),1), dict_outconv['convectivo']['Ppt_ajust'], color = 'r', linewidth = 0.8, label = 'Preciptacion Ajustada con eventos convectivos', marker = '^', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_convectivos),1), dict_outest['convectivo']['Ppt_ajust'], color = 'g', linewidth = 0.8, label = 'Preciptacion Ajustada con eventos estratiformes', marker = 'd', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_convectivos),1), dict_outmix['convectivo']['Ppt_ajust'], color = 'c', linewidth = 0.8, label = 'Preciptacion Ajustada con eventos mixtos', marker = 'o', markersize = 12, ls = '--')
plt.grid()
#plt.legend(loc = 0, fontsize =size_font )

vax = fig6.add_subplot(2,2,2)
my_xticks = map(lambda x: x[0:10],fini_estratiformes)
vax.set_xlim(-1, len(fini_estratiformes)+1)
vax.set_ylim(0, 90)
#plt.yscale('symlog')
vax.set_title('Precipitacion Acumulada - Eventos Estratiformes', fontsize = 18)
vax.set_xlabel('Fecha ocurrencia eventos', fontsize = size_font)
vax.set_ylabel('Precipitacion Acumulada (mm)', fontsize = size_font)
vax.tick_params(axis='x', labelsize= size_font)
vax.tick_params(axis='y', labelsize= size_font)
plt.xticks(np.arange(0,len(fini_estratiformes),1) + 0.5, my_xticks, rotation=330)
vax.plot(np.arange(0,len(fini_estratiformes),1), Ajustall_estratiformes, color = 'k' ,linewidth=0.8, label ='Preciptacion Ajustada con todos los eventos' , marker = '*', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_estratiformes),1), observado_estratiformes, color = 'b' ,linewidth=0.8, label ='Precipitaion Observada' , marker = 's', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_estratiformes),1), dict_outconv['estratiforme']['Ppt_ajust'], color = 'r', linewidth = 0.8, label = 'Preciptacion Ajustada con eventos convectivos', marker = '^', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_estratiformes),1), dict_outest['estratiforme']['Ppt_ajust'], color = 'g', linewidth = 0.8, label = 'Preciptacion Ajustada con eventos estratiformes', marker = 'd', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_estratiformes),1), dict_outmix['estratiforme']['Ppt_ajust'], color = 'c', linewidth = 0.8, label = 'Preciptacion Ajustada con eventos mixtos', marker = 'o', markersize = 12, ls = '--')
plt.grid()
#plt.legend(loc = 0, fontsize =size_font )

vax = fig6.add_subplot(2,1,2)
my_xticks = map(lambda x: x[0:10],fini_mixed)
vax.set_xlim(-1, len(fini_mixed)+1)
vax.set_ylim(0, 90)
#plt.yscale('symlog')
vax.set_title('Precipitacion Ajustada vs Observada - Eventos Convectivos-Estratiformes', fontsize = 18)
vax.set_xlabel('Fecha ocurrencia eventos', fontsize = size_font)
vax.set_ylabel('Precipitacion Acumulada (mm)', fontsize = size_font)
vax.tick_params(axis='x', labelsize= size_font)
vax.tick_params(axis='y', labelsize= size_font)
plt.xticks(np.arange(0,len(fini_mixed),1) + 0.5, my_xticks, rotation=330)
vax.plot(np.arange(0,len(fini_mixed),1), Ajustall_mixed, color = 'k', linewidth=2.0, label = 'Preciptacion Ajustada con todos los eventos', marker = '*', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_mixed),1), observado_mixed, color = 'b' ,linewidth=2.0, label = 'Precipitaion Observada', marker = 's', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_mixed),1), dict_outconv['mixed']['Ppt_ajust'], color = 'r', linewidth = 2.0, label = 'Preciptacion Ajustada con eventos convectivos', marker = '^', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_mixed),1), dict_outest['mixed']['Ppt_ajust'], color = 'g', linewidth = 2.0, label = 'Preciptacion Ajustada con eventos estratiformes', marker = 'd', markersize = 12, ls = '--')
vax.plot(np.arange(0,len(fini_mixed),1), dict_outmix['mixed']['Ppt_ajust'], color = 'c', linewidth = 2.0, label = 'Preciptacion Ajustada con eventos mixtos', marker = 'o', markersize = 12, ls = '--')
plt.grid()
plt.legend(loc=3, bbox_to_anchor=(0, -.57,1.0, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=2, prop={'size':16})
plt.savefig('/home/julian/Desktop/pptacum_obsvsajust.png', format='png')

size_font = 16 
plt.close('all')
plt.cla()
plt.clf()

fig6 = plt.figure(6,figsize=(20, 15))
plt.subplots_adjust(left = 0.05,right = 0.95,top = 0.95, bottom = 0.15 ,hspace = 0.35, wspace = 0.1)
vax = fig6.add_subplot(2,2,1)
my_xticks = map(lambda x: x[0:10],fini_convectivos)
vax.set_xlim(-1, len(fini_convectivos)+1)
vax.set_ylim(0, 70)
vax.set_title('Precipitacion Acumulada - Eventos Convectivos', fontsize = 18)
vax.set_xlabel('Fecha ocurrencia eventos', fontsize = size_font)
vax.set_ylabel('Precipitacion Acumulada (mm)', fontsize = size_font)
vax.tick_params(axis='x', labelsize= size_font)
vax.tick_params(axis='y', labelsize= size_font)
plt.xticks(np.arange(0,len(fini_convectivos),1) + 0.5, my_xticks, rotation=330)
vax.vlines(np.arange(0,len(fini_convectivos),1) - 0.2,[0], Ajustall_convectivos, linewidth=11, label ='Preciptacion Ajustada con todos los eventos')
vax.vlines(np.arange(0,len(fini_convectivos),1) + 0.2,[0], observado_convectivos, color = 'b' ,linewidth=11, label =  'Precipitaion Observada')
plt.grid()

vax = fig6.add_subplot(2,2,2)
my_xticks = map(lambda x: x[0:10],fini_estratiformes)
vax.set_xlim(-1, len(fini_estratiformes)+1)
vax.set_ylim(0, 70)
vax.set_title('Precipitacion Acumulada - Eventos Estratiformes', fontsize = 18)
vax.set_xlabel('Fecha ocurrencia eventos', fontsize = size_font)
vax.set_ylabel('Precipitacion Acumulada (mm)', fontsize = size_font)
vax.tick_params(axis='x', labelsize= size_font)
vax.tick_params(axis='y', labelsize= size_font)
plt.xticks(np.arange(0,len(fini_estratiformes),1) + 0.5, my_xticks, rotation=330)
vax.vlines(np.arange(0,len(fini_estratiformes),1) - 0.2,[0], Ajustall_estratiformes, linewidth=16, label = 'Preciptacion Ajustada con todos los eventos')
vax.vlines(np.arange(0,len(fini_estratiformes),1) + 0.2,[0], observado_estratiformes, color = 'b' ,linewidth=16, label = 'Precipitaion Observada')
plt.grid()

vax = fig6.add_subplot(2,1,2)
my_xticks = map(lambda x: x[0:10],fini_mixed)
vax.set_xlim(-1, len(fini_mixed)+1)
vax.set_ylim(0, 70)
vax.set_title('Precipitacion Ajustada vs Observada - Eventos Convectivos-Estratiformes', fontsize = 18)
vax.set_xlabel('Fecha ocurrencia eventos', fontsize = size_font)
vax.set_ylabel('Precipitacion Acumulada (mm)', fontsize = size_font)
vax.tick_params(axis='x', labelsize= size_font)
vax.tick_params(axis='y', labelsize= size_font)
plt.xticks(np.arange(0,len(fini_mixed),1) + 0.5, my_xticks, rotation=330)
vax.vlines(np.arange(0,len(fini_mixed),1) - 0.2,[0], Ajustall_mixed, linewidth=16, label = 'Preciptacion Ajustada con todos los eventos')
vax.vlines(np.arange(0,len(fini_mixed),1) + 0.2,[0], observado_mixed, color = 'b' ,linewidth=16, label = 'Precipitaion Observada')
plt.grid()
plt.legend(loc=3, bbox_to_anchor=(0.2, -.37,0.6, -0.3), fancybox=True, shadow=True, mode = 'expand' ,ncol=2, prop={'size':16})
plt.savefig('/home/julian/Desktop/pptacum_obsvsajust2.png', format='png')


