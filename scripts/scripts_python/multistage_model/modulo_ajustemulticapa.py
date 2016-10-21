# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Este modulo calcula un monton de cosas
# Se debe definirles como entradas: diccionario de coeficientes, data frame (polares, estaciones y disdrometro)
    # fechas iniciales de los eventos, fechas finales de los eventos.    
import numpy as np
import matplotlib
matplotlib.use('template')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import scatters_series as scs
import pandas as pd
import calculate_matches as cal_matches
import pickle 

def make_pickle(path_out, name_pkl, df_pkl):
    output_file = open(path_out+name_pkl+'.pkl', 'wb')
    pickle.dump(df_pkl, output_file)
    output_file.close()

def calculate_cuantiles(cuantiles, array_in):
    aux_cuantiles = np.array([])
    for jj in cuantiles:
        #array_in = disdro_same 
        sort_array = np.sort(array_in)
        cuantil = sort_array[round(len(array_in)*jj/100.0)]
        aux_cuantiles = np.append(aux_cuantiles, cuantil)
    return aux_cuantiles

def calculate_coef(N_bins, fecha_disdro ,date_pols,fecha_est ,ref_disdro, dbzh_s, dbzv_s, pptrate_disdro, ppt_rate, ajust_qq, str_disdro, estacion, grafica_scatters, path_plotout, pass_by_zero, write_clases = None):
    #N_bins = 15
    if (ajust_qq == 'YES'):
        clase_coinc_pre = cal_matches.coincidentes(fecha1 =fecha_disdro , fecha2 = date_pols, serie1 = ref_disdro , serie2 = dbzh_s)
        dict_disdrovsdbzh_pre = clase_coinc_pre.find_matches(return_coincidents = True)
        
        deciles = np.arange(10,100,10)    
        ref_same = dict_disdrovsdbzh_pre['serie2_same']
        disdro_same = dict_disdrovsdbzh_pre['serie1_same']
        filtro_nan = np.isnan(ref_same)
        ref_same_new = ref_same[(filtro_nan == False) & (disdro_same != -9.9)]
        disdro_same_new = disdro_same[(filtro_nan == False) & (disdro_same != -9.9)]
        
        deciles_disdro = calculate_cuantiles(cuantiles = deciles , array_in = disdro_same_new)
        deciles_radar = calculate_cuantiles(cuantiles = deciles, array_in = ref_same_new)
        dict_regqq = cal_matches.make_regresion(deciles_radar, deciles_disdro)
        
        qq_dbzh_s = dict_regqq['pendiente']*dbzh_s + dict_regqq['intercepto']
    
    else:
        qq_dbzh_s = np.copy(dbzh_s)
        
    clase_coinc = cal_matches.coincidentes(fecha1 =fecha_disdro , fecha2 = date_pols, serie1 = ref_disdro , serie2 = qq_dbzh_s)
    dict_disdrovsdbzh = clase_coinc.find_matches(return_coincidents = True)
    est_disdrovsdbzh = clase_coinc.ajust_bins(nbins = N_bins)
    reg_disdrovsdbzh = cal_matches.make_regresion(est_disdrovsdbzh['bins'],est_disdrovsdbzh['medianas'])
    regmadmin_disdrovsdbzh = cal_matches.make_regresion(est_disdrovsdbzh['bins'],est_disdrovsdbzh['medianas'] - est_disdrovsdbzh['MAD'])
    regmadmax_disdrovsdbzh = cal_matches.make_regresion(est_disdrovsdbzh['bins'],est_disdrovsdbzh['medianas'] + est_disdrovsdbzh['MAD'])
    if (write_clases is not None):
        make_pickle('/home/julian/Desktop/', 'calses_capa1', est_disdrovsdbzh['dic_clase'])

    clase_coinc2 = cal_matches.coincidentes(fecha1 =fecha_disdro ,fecha2 = date_pols, serie1 = ref_disdro , serie2 = dbzv_s)
    dict_disdrovsdbzv = clase_coinc2.find_matches(return_coincidents = True)
    est_disdrovsdbzv = clase_coinc2.ajust_bins(nbins = N_bins)
    reg_disdrovsdbzv = cal_matches.make_regresion(est_disdrovsdbzv['bins'],est_disdrovsdbzv['medianas'])
    regmadmin_disdrovsdbzv = cal_matches.make_regresion(est_disdrovsdbzv['bins'],est_disdrovsdbzv['medianas'] - est_disdrovsdbzv['MAD'])
    regmadmax_disdrovsdbzv = cal_matches.make_regresion(est_disdrovsdbzv['bins'],est_disdrovsdbzv['medianas'] + est_disdrovsdbzv['MAD'])

    clase_coinc3 = cal_matches.coincidentes(fecha1 = fecha_disdro, fecha2 = fecha_disdro, serie1 = ref_disdro, serie2 = pptrate_disdro)
    dict_disdro = clase_coinc3.find_matches(return_coincidents = True)
    est_disdro = clase_coinc3.ajust_bins(nbins = N_bins)
    reg_disdro = cal_matches.make_regresion(np.log10(est_disdro['medianas']),(est_disdro['bins'])/10.0)
    regmadmin_disdro = cal_matches.make_regresion(np.log10(est_disdro['medianas'] - est_disdro['MAD']),est_disdro['bins']/10.0)
    regmadmax_disdro = cal_matches.make_regresion(np.log10(est_disdro['medianas'] + est_disdro['MAD']),est_disdro['bins']/10.0)
    if (write_clases is not None):
        make_pickle('/home/julian/Desktop/', 'calses_capa2', est_disdro['dic_clase'])

    clase_coinc4 = cal_matches.coincidentes(fecha1 = fecha_disdro, fecha2 = fecha_est, serie1 = pptrate_disdro, serie2 = ppt_rate)
    dict_disdrovsest = clase_coinc4.find_matches(return_coincidents = True)
    est_disdrovsest = clase_coinc4.ajust_bins(nbins = N_bins)
    if pass_by_zero == 'YES':
        (est_disdrovsest['bins'])[0] = 0.0
        (est_disdrovsest['medianas'])[0] = 0.0 
        reg_disdrovsest = cal_matches.make_regresion_by_origin(est_disdrovsest['bins'],est_disdrovsest['medianas'])
    else:
        reg_disdrovsest = cal_matches.make_regresion(est_disdrovsest['bins'],est_disdrovsest['medianas'])
    #print reg_disdrovsest
    regmadmin_disdrovsest = cal_matches.make_regresion(est_disdrovsest['bins'],est_disdrovsest['medianas'] - est_disdrovsest['MAD'])
    regmadmax_disdrovsest = cal_matches.make_regresion(est_disdrovsest['bins'],est_disdrovsest['medianas'] + est_disdrovsest['MAD'])
    if (write_clases is not None):
        make_pickle('/home/julian/Desktop/', 'calses_capa3', est_disdrovsest['dic_clase'])

    if grafica_scatters == 'YES':
        plt.cla()
        plt.clf()
        plt.close()
        size = 11
        fig1 = plt.figure(1)
        fig1.set_figheight(10)
        fig1.set_figwidth(10)
        #fig1.suptitle('Evento del '+fecha_leida+'-- Estacion:'+estacion, fontsize=14)
        plt.subplots_adjust(left = 0.1,right = 0.91,top = 0.95, bottom = 0.1,hspace = 0.5, wspace = 0.3)
        ax1 = fig1.add_subplot(2,2,1)
        scs.pinta_scatterplots(ax = ax1, size = 11, str_labelx ='Reflectividad Disdrometro $(dBZ)$', str_labely = 'Reflectividad horizontal Radar $(dBZ)$',\
                        seriex = dict_disdrovsdbzh['serie1_same'], seriey = dict_disdrovsdbzh['serie2_same'], marca = 'x', size_marca = 8 , color_marca = 'k', legend_scatter = 'Radar vs Disdrometro',\
                            yscale_log = False, other = False, xlim_sup = 50, xlim_inf = 0, ylim_sup = 50, ylim_inf = 0, seriex2 = None, seriey2=None, size_marca2=None,\
                                marca2=None,color_marca2 = None, legend_scatter2 = None)
        ax1.plot(dict_disdrovsdbzh['serie1_same'], dict_disdrovsdbzh['serie1_same'], color = 'k', linestyle = '--' ) 
        ax1.scatter(est_disdrovsdbzh['bins'], est_disdrovsdbzh['medianas'], s = 45, marker = 'o' , c = 'y', label = 'Mediana por intervalos en x')
        ax1.scatter(est_disdrovsdbzh['bins'], est_disdrovsdbzh['q75'], s = 25, marker = 'D' , c = 'r', label = 'Cuantil del 25% y 75%')
        ax1.scatter(est_disdrovsdbzh['bins'], est_disdrovsdbzh['q25'], s = 25, marker = 'D' , c = 'r')
        ax1.scatter(est_disdrovsdbzh['bins'], est_disdrovsdbzh['medianas'] - est_disdrovsdbzh['MAD'],  s = 35, marker = 'v' , c = 'c', label = 'Mediana mas o menos 1MAD')
        ax1.scatter(est_disdrovsdbzh['bins'], est_disdrovsdbzh['medianas'] + est_disdrovsdbzh['MAD'],  s = 35, marker = 'v', c = 'c')
        plt.grid()
        plt.legend(loc=3, bbox_to_anchor=(-0.1, -0.45,1.2, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=1, prop={'size':10})

        ax2 = fig1.add_subplot(2,2,2)
        ax2.set_xlim(0,50)
        ax2.set_ylim(0,50)
        ax2.set_xlabel('Reflectividad Disdrometro $(dBZ)$', fontsize = 11)
        ax2.set_ylabel('Reflectividad horizontal Radar $(dBZ)$', fontsize = 11)
        ax2.scatter(est_disdrovsdbzh['bins'], est_disdrovsdbzh['medianas'], s = 35, marker = 'o' , c = 'k', label = 'Mediana por intervalos en x')
        aux_regl = np.arange(0,100,1)
        rsqrt2 = '%0.3f'%((np.corrcoef(est_disdrovsdbzh['bins'], est_disdrovsdbzh['medianas'] - est_disdrovsdbzh['MAD']))[0,1])**2.0
        m2_str = '%0.3f'%(reg_disdrovsdbzh['pendiente'])
        I2_str = '%0.3f'%(reg_disdrovsdbzh['intercepto'])
        ax2.plot(aux_regl, reg_disdrovsdbzh['pendiente']*aux_regl + reg_disdrovsdbzh['intercepto'], c = 'k', linewidth = 2.0, label = 'Ajuste: m='+str(m2_str)+' b='+str(I2_str)+ ' $R^2$='+str(rsqrt2)) 
        ax2.plot(aux_regl, regmadmin_disdrovsdbzh['pendiente']*aux_regl + regmadmin_disdrovsdbzh['intercepto'], c = 'c', linewidth = 2.0)
        ax2.plot(aux_regl, regmadmax_disdrovsdbzh['pendiente']*aux_regl + regmadmax_disdrovsdbzh['intercepto'], c = 'c', linewidth = 2.0)
        ax2.scatter(est_disdrovsdbzh['bins'], est_disdrovsdbzh['q75'], s = 20, marker = 'D' , c = 'r', label = 'Cuantil del 25% y 75%')
        ax2.scatter(est_disdrovsdbzh['bins'], est_disdrovsdbzh['q25'], s = 20, marker = 'D' , c = 'r')
        plt.grid()
        plt.legend(loc=3, bbox_to_anchor=(-0.1, -0.45,1.2, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=1, prop={'size':10})
        
        ax3 = fig1.add_subplot(3,1,3)
        ax3.set_title(u'Comportamiento de las medidas de desviación')
        ax3.set_xlim(0, 50)
        ax3.set_ylim(0, 30)
        ax3.tick_params(axis='x', labelsize = 11)
        ax3.tick_params(axis='y', labelsize = 11)
        ax3.set_xlabel(u'Reflectividad Horizontal (dBZ)', fontsize = size)
        ax3.set_ylabel(u'Desviación (dBZ)', fontsize = size)
        ax3.plot(est_disdrovsdbzh['bins'], est_disdrovsdbzh['MAD'], color = 'r', lw = 1.5 ,label = 'Mediana de las desviaciones absolutas (MAD)')
        ax3.plot(est_disdrovsdbzh['bins'], est_disdrovsdbzh['q75'] - est_disdrovsdbzh['q25'], color = 'c', lw = 1.5,label = 'Rango inter cuartil (IQR)')
        plt.grid()
        plt.legend(loc=3, bbox_to_anchor=(0.1, -0.35,0.8, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=2, prop={'size':10})
        
        plt.savefig(path_plotout+'Ajuste_Refdisdro'+str_disdro+'vsdBzH.pdf', format ='pdf', dpi = 250)
        
        ## ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        plt.cla()
        plt.clf()
        plt.close()
        #fig1 = plt.figure(1, figsize = (8.27, 11.2))
        fig2 = plt.figure(2)
        fig2.set_figheight(10)
        fig2.set_figwidth(10)
        plt.subplots_adjust(left = 0.1,right = 0.91,top = 0.95, bottom = 0.1,hspace = 0.5, wspace = 0.3)
        ax3 = fig2.add_subplot(2,2,1)
        scs.pinta_scatterplots(ax = ax3, size = 10, str_labelx = 'Reflectividad Disdrometro $(dBZ)$', str_labely = 'Reflectividad vertical Radar $(dBZ)$',\
                        seriex = dict_disdrovsdbzv['serie1_same'], seriey = dict_disdrovsdbzv['serie2_same'], marca = 'x', size_marca = 15, color_marca = 'k', legend_scatter = 'Radar vs Disdrometro',\
                            yscale_log = False, other = False, xlim_sup = 50, xlim_inf = 0, ylim_sup = 50, ylim_inf = 0, seriex2 = None, seriey2=None, size_marca2=None,\
                                marca2=None,color_marca2 = None, legend_scatter2 = None)
        ax3.plot(dict_disdrovsdbzv['serie1_same'], dict_disdrovsdbzv['serie1_same'], color = 'k', linestyle = '--' ) 
        ax3.scatter(est_disdrovsdbzv['bins'], est_disdrovsdbzv['medianas'], s = 45, marker = 'o' , c = 'y', label = 'Mediana por intervalos en x')
        ax3.scatter(est_disdrovsdbzv['bins'], est_disdrovsdbzv['q75'], s = 25, marker = 'D' , c = 'r', label = 'Cuantil del 25% y 75%')
        ax3.scatter(est_disdrovsdbzv['bins'], est_disdrovsdbzv['q25'], s = 25, marker = 'D' , c = 'r')
        ax3.scatter(est_disdrovsdbzv['bins'], est_disdrovsdbzv['medianas'] - est_disdrovsdbzv['MAD'],  s = 35, marker = 'v' , c = 'c', label = 'Mediana mas o menos 1MAD')
        ax3.scatter(est_disdrovsdbzv['bins'], est_disdrovsdbzv['medianas'] + est_disdrovsdbzv['MAD'],  s = 35, marker = 'v', c = 'c')
        plt.grid()
        plt.legend(loc=3, bbox_to_anchor=(-0.1, -0.45,1.2, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=1, prop={'size':10})

        ax4 = fig2.add_subplot(2,2,2)
        ax4.set_xlim(0,50)
        ax4.set_ylim(0,50)
        ax4.set_xlabel('Reflectividad Disdrometro $(dBZ)$', fontsize = 10)
        ax4.set_ylabel('Reflectividad vertical Radar $(dBZ)$', fontsize = 10)
        ax4.scatter(est_disdrovsdbzv['bins'], est_disdrovsdbzv['medianas'], s = 35, marker = 'o' , c = 'k', label = 'Mediana por intervalos en x')
        aux_regl = np.arange(0,100,1)
        rsqrt4 = '%0.3f'%((np.corrcoef(est_disdrovsdbzv['bins'], est_disdrovsdbzv['medianas'] - est_disdrovsdbzv['MAD']))[0,1])**2.0
        m4_str = '%0.3f'%(reg_disdrovsdbzv['pendiente'])
        I4_str = '%0.3f'%(reg_disdrovsdbzv['intercepto'])
        ax4.plot(aux_regl, reg_disdrovsdbzv['pendiente']*aux_regl + reg_disdrovsdbzv['intercepto'], c = 'k', linewidth = 2.0, label = 'Ajuste: m='+str(m4_str)+' b='+str(I4_str)+ ' $R^2$='+str(rsqrt4)) 
        ax4.plot(aux_regl, regmadmin_disdrovsdbzv['pendiente']*aux_regl + regmadmin_disdrovsdbzv['intercepto'], c = 'c', linewidth = 2.0)
        ax4.plot(aux_regl, regmadmax_disdrovsdbzv['pendiente']*aux_regl + regmadmax_disdrovsdbzv['intercepto'], c = 'c', linewidth = 2.0)
        ax4.scatter(est_disdrovsdbzv['bins'], est_disdrovsdbzv['q75'], s = 20, marker = 'D' , c = 'r', label = 'Cuantil del 25% y 75%')
        ax4.scatter(est_disdrovsdbzv['bins'], est_disdrovsdbzv['q25'], s = 20, marker = 'D' , c = 'r')
        plt.grid()
        plt.legend(loc=3, bbox_to_anchor=(-0.1, -0.45,1.2, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=1, prop={'size':10})
        
        ax3 = fig2.add_subplot(3,1,3)
        ax3.set_title(u'Comportamiento de las medidas de desviación')
        ax3.set_xlim(0, 50)
        ax3.set_ylim(0, 30)
        ax3.tick_params(axis='x', labelsize = 11)
        ax3.tick_params(axis='y', labelsize = 11)
        ax3.set_xlabel(u'Reflectividad Vertical (dBZ)', fontsize = size)
        ax3.set_ylabel(u'Desviación (dBZ)', fontsize = size)
        ax3.plot(est_disdrovsdbzv['bins'],est_disdrovsdbzv['MAD'], color = 'r', lw = 1.5 ,label = 'Mediana de las desviaciones absolutas (MAD)')
        ax3.plot(est_disdrovsdbzv['bins'], est_disdrovsdbzv['q75'] - est_disdrovsdbzv['q25'], color = 'c', lw = 1.5,label = 'Rango inter cuartil (IQR)')
        plt.grid()
        plt.legend(loc=3, bbox_to_anchor=(0.1, -0.35,0.8, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=2, prop={'size':10})
        plt.savefig(path_plotout+'Ajuste_Refdisdro'+str_disdro+'vsdBzV.pdf', format ='pdf', dpi = 250)

        plt.cla()
        plt.clf()
        plt.close()
        fig3 = plt.figure(3)
        fig3.set_figheight(10)
        fig3.set_figwidth(10)
        size = 14
        plt.subplots_adjust(left = 0.1,right = 0.91,top = 0.95, bottom = 0.1,hspace = 0.5, wspace = 0.3)
        ax5 = plt.subplot2grid((3,1), (0, 0), rowspan=2)
        ax5.set_xlabel(u'Reflectividad Disdrómetro $(dBZ)$', fontsize = size)
        ax5.set_ylabel(u'Intensidad precipitacion disdrómetro $[mm/h]$', fontsize = size)
        ax5.set_ylim(-2, 100)
        ax5.set_xlim(0, 55)
        ax5.tick_params(axis='x', labelsize=size)
        ax5.tick_params(axis='y', labelsize=size)
        plt.scatter(ref_disdro,pptrate_disdro , s=20, marker='x', c='k', label = u'Intensidad precipitación disdrómetro vs Reflectividad disdrómetro')
        ax5.scatter(est_disdro['bins'], est_disdro['medianas'], s = 60, marker = 'o' , c = 'y', label = 'Mediana por intervalos en x')
        ax5.scatter(est_disdro['bins'], est_disdro['q75'], s = 45. , marker = 'D' ,c = 'r', label = 'Cuantil del 25% y 75%')
        ax5.scatter(est_disdro['bins'], est_disdro['q25'], s = 45  , marker = 'D', c = 'r')
        ax5.plot(est_disdro['bins'], est_disdro['medianas'] - est_disdro['MAD'], marker = 'v', markersize = 6, c = 'c', label = 'Mediana mas o menos 1MAD')
        ax5.plot(est_disdro['bins'], est_disdro['medianas'] + est_disdro['MAD'], marker = 'v', markersize = 6,  c = 'c')
        plt.grid()
        plt.legend(loc = 2, fontsize=12)
        
        ax6 = plt.subplot2grid((3,1), (2, 0), rowspan=1)
        ax6.set_title(u'Comportamiento de las medidas de desviación')
        ax6.set_xlim(0, 55)
        ax6.set_ylim(0, 45)
        ax6.tick_params(axis='x', labelsize = size)
        ax6.tick_params(axis='y', labelsize = size)
        ax6.set_xlabel(u'Reflectividad (dBZ)', fontsize = size)
        ax6.set_ylabel(u'Desviación (mm/h)', fontsize = size)
        ax6.plot(est_disdro['bins'], est_disdro['MAD'], marker = 'v' , markersize = 7, color = 'c', lw = 1.5 ,label = 'Mediana de las desviaciones absolutas (MAD)')
        ax6.plot(est_disdro['bins'], est_disdro['q75'] - est_disdro['q25'],marker = 'D' , markersize = 7,color = 'r', lw = 1.5,label = 'Rango intercuartil (IQR)')
        plt.grid()
        plt.legend(loc=3, bbox_to_anchor=(0, -0.45,1, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=2, prop={'size':12})
        plt.savefig(path_plotout+'Ajuste_Refdisdro'+str_disdro+'vsPPt_ratedisdro.pdf', format ='pdf', dpi = 250)
        
        #print 'guarde los cambios'
        plt.cla()
        plt.clf()
        plt.close()
        fig4 = plt.figure(4)
        fig4.set_figheight(10)
        fig4.set_figwidth(10)
        plt.subplots_adjust(left = 0.1,right = 0.91,top = 0.95, bottom = 0.1,hspace = 1.0, wspace = 0.3)
        ax7 = plt.subplot2grid((3,1), (0, 0), rowspan=2)
        scs.pinta_scatterplots(ax = ax7, size = 14, str_labelx =u'Intensidad precipitacion disdrómetro $[mm/h]$' , str_labely = u'Intensidad precipitacion estación $[mm/h]$)',\
                        seriex = dict_disdrovsest['serie1_same'], seriey = dict_disdrovsest['serie2_same'], marca = 'x', size_marca = 15, color_marca = 'k', legend_scatter = u'Disdrómetro vs Estación',\
                            yscale_log = False, other = False, xlim_sup = 75, xlim_inf = 0, ylim_sup = 120, ylim_inf = 0, seriex2 = None, seriey2=None, size_marca2=None,\
                                marca2=None,color_marca2 = None, legend_scatter2 = None)
        ax7.scatter(est_disdrovsest['bins'], est_disdrovsest['medianas'], s = 55, marker = 'o' , c = 'y', label = 'Mediana por intervalos en x')
        ax7.scatter(est_disdrovsest['bins'], est_disdrovsest['q75'], s = 45, marker = 'D' , c = 'r', label = 'Cuantil del 10% y 90 %')
        ax7.scatter(est_disdrovsest['bins'], est_disdrovsest['q25'], s = 45, marker = 'D' , c = 'r')
        ax7.plot(est_disdrovsest['bins'], est_disdrovsest['medianas'] - est_disdrovsest['MAD'], marker = 'v', markersize = 6, c = 'c', label = 'Mediana mas o menos 1MAD')
        ax7.plot(est_disdrovsest['bins'], est_disdrovsest['medianas'] + est_disdrovsest['MAD'], marker = 'v', markersize = 6, c = 'c')
        plt.grid()
        plt.legend(loc=3, bbox_to_anchor=(0.0, -0.25, 1.0, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=2, prop={'size':11})
       
        ax8 = plt.subplot2grid((3,1), (2, 0), rowspan=1)
        ax8.set_title(u'Comportamiento de las medidas de desviación')
        ax8.set_xlim(0, 70)
        ax8.set_ylim(0, 50)
        ax8.tick_params(axis='x', labelsize = size)
        ax8.tick_params(axis='y', labelsize = size)
        ax8.set_xlabel(u'Intensidad de precipitación $(mm/h)$', fontsize = size)
        ax8.set_ylabel(u'Desviación $(mm/h)$', fontsize = size)
        ax8.plot(est_disdrovsest['bins'],est_disdrovsest['MAD'], marker = 'v' , markersize = 7, color = 'c', lw = 1.5 ,label = u'Mediana de las desviaciones absolutas (MAD)')
        ax8.plot(est_disdrovsest['bins'], est_disdrovsest['q75'] - est_disdrovsest['q25'],marker = 'D' , markersize = 7,color = 'r', lw = 1.5,label = u'Rango intercuartil (IQR)')
        plt.grid()
        plt.legend(loc=3, bbox_to_anchor=(0, -0.55,1, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=2, prop={'size':12})
        plt.savefig(path_plotout+'Ajuste_pptratedisdro'+str_disdro+'vsPPt_rate'+estacion+'.pdf', format ='pdf', dpi = 250)

    dict_coef = {'capa1':{'mc1':reg_disdrovsdbzh['pendiente'],'bc1':reg_disdrovsdbzh['intercepto'],'Emin_m':regmadmin_disdrovsdbzh['pendiente'],'Emin_b':regmadmin_disdrovsdbzh['intercepto'] ,'Emax_m':regmadmax_disdrovsdbzh['pendiente'] ,'Emax_b':regmadmax_disdrovsdbzh['intercepto'] },\
        'capa2':{'mc2':reg_disdro['pendiente'],'bc2':10**reg_disdro['intercepto'],'Emin_m':regmadmin_disdro['pendiente'] ,'Emin_b':10**regmadmin_disdro['intercepto'] ,'Emax_m':regmadmax_disdro['pendiente'] ,'Emax_b':10**regmadmax_disdro['intercepto'] },\
            'capa3':{'mc3':reg_disdrovsest['pendiente'],'bc3':reg_disdrovsest['intercepto'],'Emin_m':regmadmin_disdrovsest['pendiente'] ,'Emin_b':regmadmin_disdrovsest['intercepto'] ,'Emax_m':regmadmax_disdrovsest['pendiente'] ,'Emax_b':regmadmax_disdrovsest['intercepto']}}
    #print dict_coef
    return dict_coef

def ajuste_multicapa(dict_coef, polar_data, est_data,disdro_data, fini_str, ffin_str, tipo_str,res_resample, width_smooth, make_grafica ,trunc = None):

    Ajustall_convectivos = np.array([])
    observado_convectivos = np.array([])
    fini_convectivos = np.array([])
    ffin_convectivos = np.array([])

    Ajustall_estratiformes = np.array([])
    observado_estratiformes = np.array([])
    fini_estratiformes = np.array([])
    ffin_estratiformes = np.array([])

    Ajustall_mixed = np.array([])
    observado_mixed = np.array([])
    fini_mixed = np.array([])
    ffin_mixed = np.array([])

    for kk in range(len(fini_str)):
        polardata_evento = polar_data[fini_str[kk]:ffin_str[kk]]
        estdata_evento = est_data[fini_str[kk]:ffin_str[kk]]
        disdrodata_evento = disdro_data[fini_str[kk]:ffin_str[kk]]
        
        #ppt_5min = estdata_evento.groupby(estdata_evento.index.map(lambda t: datetime.datetime(t.year, t.month, t.day, t.hour))).sum()
        ppt_5min = estdata_evento.resample("'"+res_resample+"'", how="mean", label = 'right',closed = 'right')

        dbzh_s_evento = polardata_evento.dbzh.values
        date_pols_evento = polardata_evento.index 

        ppt_int_evento = ppt_5min.ppt_int.values
        fecha_est_evento = ppt_5min.index

        Trunc_dbzh_s = np.copy(dbzh_s_evento)

        cal_capa1 = (1/dict_coef['capa1']['mc1'])*Trunc_dbzh_s - (dict_coef['capa1']['bc1']/dict_coef['capa1']['mc1'])
        if trunc is not None:
            cal_capa1[cal_capa1 >= trunc] = trunc
        cal_capa2 = ((10**(cal_capa1/10.0))/dict_coef['capa2']['bc2'])**(1.0/(dict_coef['capa2']['mc2']))
        cal_capa3 = (dict_coef['capa3']['mc3']*cal_capa2 + dict_coef['capa3']['bc3'])
        cal_capa3[cal_capa1 <= 10.0] = 0.0

        mask_ajust = np.isnan(cal_capa3)
        cal_capa3[mask_ajust == True] = 0 
        cal_capa3[cal_capa3 < 0] = 0

        # Se hace una media movil por evento 
        size_smooth = int(width_smooth)
        limit_smooth = int(np.floor(size_smooth/2.0))
        ajust_smooth = np.array([])
        for ii in range(len(cal_capa3)):
            if (ii-limit_smooth) >= 0:
                aux_smooth =np.array(cal_capa3[ii-limit_smooth: ii+limit_smooth+1])
                element_smooth = np.mean(aux_smooth) 
            else:
                element_smooth = 0
            ajust_smooth = np.append(ajust_smooth, element_smooth)
            
        mask_obs = np.isnan(ppt_int_evento)
        acum_ajuste = ajust_smooth/12.0
        acum_observados = ppt_int_evento[mask_obs == False]/12.0
        #print 'acumulado observad'
        #print 
        #print 'acumulado ajustado'
        #print 

        try:
            #print 'Lo observado es:', str(np.sum(acum_observados))
            #print 'Lo modelado sera:', str(np.sum(acum_ajuste))
            #print str((np.abs(np.sum(acum_ajuste)-np.sum(acum_observados))/np.sum(acum_observados))*100.0)+' %'

            if make_grafica == 'YES':
                plt.close('all')
                plt.cla()
                plt.clf()
                size = 9
                fig5 = plt.figure(5)
                fig5.set_figheight(5)
                fig5.set_figwidth(10)
                plt.subplots_adjust(left = 0.1,right = 0.91,top = 0.95, bottom = 0.22,hspace = 1.0, wspace = 0.3)
                #fig1 = plt.figure(1, figsize = (8.27, 11.2))
                #fig1.suptitle('Evento del '+fecha_leida+'-- Estacion:'+estacion, fontsize=14)
                plt.subplots_adjust(hspace = 0.5)
                ax1 = fig5.add_subplot(1, 1, 1)
                scs.pinta_series (ax1, size = size, str_labelx = 'Tiempo', str_labely = u'Intensidad de precipitación $(mm/h)$',\
                    seriex1 =fecha_est_evento , seriey1 = ppt_int_evento, legends1 = u'Intensidad de Precipitación Observada', seriex2 = date_pols_evento, seriey2 = ajust_smooth, legends2 = u'Intensidad de Precipitación Estimada',\
                        twinx = False, str_labelty = None, serietx = None,seriety = None, legendst = None,\
                            ylim_inf = 0, ylim_sup =110, tylim_inf = 0 , tylim_sup = 150, Lwidth = 1.0)
                ax1.fill_between( fecha_est_evento, ppt_int_evento, 0.0, where = ppt_int_evento > 0.0 , color = 'Grey', alpha = 0.4 ,interpolate=True)
                ax1.fill_between( date_pols_evento, ajust_smooth, 0.0, where = ajust_smooth > 0.0 , color = 'red', alpha = 0.3 ,interpolate=True)
                
                axt = ax1.twinx()
                axt.set_ylabel(u'Precipitación acumulada $(mm)$', fontsize = size)
                axt.tick_params(axis='y', labelsize=size)
                axt.set_ylim(0,60.0)
                axt.plot(fecha_est_evento,np.cumsum(acum_observados), c = 'b', lw = 1.5, ls = '--', label = u'Precipitación acumulada observada')
                axt.plot(date_pols_evento, np.cumsum(acum_ajuste), c = 'm', lw = 1.5, ls = '--', label = u'Precipitación acumulada ajustada' )
                h1, l1 = ax1.get_legend_handles_labels()
                h2, l2 = axt.get_legend_handles_labels()            
                plt.legend(h1+h2, l1+l2,loc=3, bbox_to_anchor=(0.0, -0.3,1.0, -0.5), fancybox=True, shadow=True, mode = 'expand' ,ncol=2, prop={'size':10})
                #plt.grid()
                plt.savefig('/home/julian/Desktop/ajuste_'+(fini_str[kk])[0:10]+'_'+tipo_str[kk]+'.png', format = 'png', dpi = 500)
        except:
            pass

        
        if (tipo_str[kk] == 'convectivo'):
            Ajustall_convectivos = np.append(Ajustall_convectivos, np.sum(acum_ajuste))
            observado_convectivos = np.append(observado_convectivos, np.sum(acum_observados))
            fini_convectivos = np.append(fini_convectivos, fini_str[kk])
            ffin_convectivos = np.append(ffin_convectivos, ffin_str[kk])
        
        if (tipo_str[kk] == 'estratiforme'):
            Ajustall_estratiformes = np.append(Ajustall_estratiformes, np.sum(acum_ajuste))
            observado_estratiformes = np.append(observado_estratiformes, np.sum(acum_observados))
            fini_estratiformes = np.append(fini_estratiformes, fini_str[kk])
            ffin_estratiformes = np.append(ffin_estratiformes, ffin_str[kk])
            
        if (tipo_str[kk] == 'convectivo-estratiforme'):
            Ajustall_mixed = np.append(Ajustall_mixed, np.sum(acum_ajuste))
            observado_mixed = np.append(observado_mixed, np.sum(acum_observados))
            fini_mixed = np.append(fini_mixed, fini_str[kk])
            ffin_mixed = np.append(ffin_mixed, ffin_str[kk])
            
    dict_salida = {'convectivo':{'Ppt_ajust':Ajustall_convectivos,'Ppt_observada':observado_convectivos,'fini':fini_convectivos,'ffin':ffin_convectivos},\
        'estratiforme':{'Ppt_ajust':Ajustall_estratiformes,'Ppt_observada':observado_estratiformes,'fini':fini_estratiformes,'ffin':ffin_estratiformes},\
            'mixed':{'Ppt_ajust':Ajustall_mixed,'Ppt_observada':observado_mixed,'fini':fini_mixed,'ffin':ffin_mixed}}  
    
    return dict_salida
