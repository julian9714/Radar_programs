# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -----------------------------------------------------
# Esto es una prueba
# Import necessary packages
import sys
sys.path.append('/home/julian/Dropbox/QPE/scripts/scripts_python/modulos_generales/')

import numpy as np
import glob  
import useful_toolbox as mytools
import calculate_matches as cal_m
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as colors

class plotter_zr(object):
    def __init__(self, path_st, name_st, source):
        self.path_st = path_st
        self.name_st = name_st
        self.source  = source
    def get_data(self):
        list_files   = sorted(glob.glob(self.path_st+self.name_st))
        #print self.path_st+self.name_st
        #print list_files
        if self.source == 'Disdrometro':
            print self.name_st
            pkl_data_ppt     = mytools.open_pklfiles(list_files[0])
            if (self.name_st == '77_*.pkl'): 
                str_corresp = '60_polarimetric.pkl' 
            if (self.name_st == '78_*.pkl'):
                str_corresp = '33_polarimetric.pkl' 
            if (self.name_st == '80_*.pkl'):
                str_corresp = '207_polarimetric.pkl' 
            if (self.name_st == '131_*.pkl'):
                str_corresp = '204_polarimetric.pkl'
            list_files2   = sorted(glob.glob(self.path_st+str_corresp))
            print self.name_st
            print str_corresp
            print list_files2
            pkl_data_polar = mytools.open_pklfiles(list_files2[0])

            date_polar_dummy  = pkl_data_polar.index
            ref_polar_dummy   = pkl_data_polar.dbzh.values
            self.date_polar  = date_polar_dummy[ref_polar_dummy <= 90.]
            self.ref_polar   = ref_polar_dummy[ref_polar_dummy <= 90.]
            self.ze_polar    = 10.0 **(self.ref_polar/10.)
            date_ppt_dummy   = pkl_data_ppt.index
            data_ppt_dummy   = pkl_data_ppt.ppt_all.values
            self.date_ppt    = date_ppt_dummy[data_ppt_dummy <= 200.]
            self.data_ppt    = data_ppt_dummy[data_ppt_dummy <= 200.]

        else:
            pkl_data_polar   = mytools.open_pklfiles(list_files[0])
            pkl_data_ppt     = mytools.open_pklfiles(list_files[1])
                        
            date_polar_dummy  = pkl_data_polar.index
            ref_polar_dummy   = pkl_data_polar.dbzh.values
            self.date_polar  = date_polar_dummy[ref_polar_dummy <= 90.]
            self.ref_polar   = ref_polar_dummy[ref_polar_dummy <= 90.]
            self.ze_polar    = 10.0 **(self.ref_polar/10.)
            date_ppt_dummy   = pkl_data_ppt.index
            data_ppt_dummy   = pkl_data_ppt.ppt_int.values
            self.date_ppt    = date_ppt_dummy[data_ppt_dummy <= 200.]
            self.data_ppt    = data_ppt_dummy[data_ppt_dummy <= 200.]
    def calculate_matches_with_time_resample(self, resolution, how_res):

        #print np.amin(self.data_ppt)
        #print np.amax(self.data_ppt)
        #print np.amin(self.ze_polar)
        #print np.amax(self.ze_polar)

        if resolution == 'Original':
            matches            = cal_m.coincidentes(self.date_ppt, self.date_polar,\
                                                    self.data_ppt, self.ze_polar)
            struct_matches     = matches.find_matches(return_coincidents = True)
            aux_structmatches  = {'Ppt_rate':struct_matches['serie1_same'],'Ze':struct_matches['serie2_same']}
            
            pd_macthes    = pd.DataFrame(aux_structmatches, index = struct_matches['fecha_same'])
        else:
            aux_df_ze_5min     = pd.DataFrame({'Ze':self.ze_polar}, index = self.date_polar)
            aux_df_pptrate     = pd.DataFrame({'Ppt_rate':self.data_ppt}, index = self.date_ppt)
            aux_df_pptrate_5min= aux_df_pptrate.resample("5MIN", how = 'mean', label = 'right',closed = 'right')
                        
            if (how_res == 'Regular'):
                aux_df_ze_res      = aux_df_ze_5min.resample(resolution+"MIN", how = 'mean', label = 'right',\
                                     closed = 'right')
                aux_df_pptrate_res = aux_df_pptrate_5min.resample(resolution+"MIN", how = 'mean',\
                                    label = 'right', closed = 'right')
                 
                matches            = cal_m.coincidentes(aux_df_pptrate_res.index,\
                                                        aux_df_ze_res.index,\
                                                        aux_df_pptrate_res.Ppt_rate.values,\
                                                        aux_df_ze_res.Ze.values)
                struct_matches     = matches.find_matches(return_coincidents = True)
                aux_structmatches  = {'Ppt_rate':struct_matches['serie1_same'],'Ze':struct_matches['serie2_same']}
                pd_macthes    = pd.DataFrame(aux_structmatches, index = struct_matches['fecha_same'])
            if (how_res == 'Rolling'):
                wind = int(int(resolution)/5.0)
                min_wind = round(0.7*wind)

                aux_df_ze_res      = pd.rolling_mean(aux_df_ze_5min, window = wind, min_periods= min_wind)
                aux_df_pptrate_res = pd.rolling_mean(aux_df_pptrate_5min, window = wind, min_periods= min_wind)
                 
                matches            = cal_m.coincidentes(aux_df_pptrate_res.index,\
                                                        aux_df_ze_res.index,\
                                                        aux_df_pptrate_res.Ppt_rate.values,\
                                                        aux_df_ze_res.Ze.values)
                struct_matches     = matches.find_matches(return_coincidents = True)
                aux_structmatches  = {'Ppt_rate':struct_matches['serie1_same'],'Ze':struct_matches['serie2_same']}
                pd_macthes    = pd.DataFrame(aux_structmatches, index = struct_matches['fecha_same'])
        
        ppt_same = pd_macthes.Ppt_rate.values
        ze_same  = pd_macthes.Ze.values
        
        ppt_mask = ppt_same[(np.isnan(ze_same) == False) & (ppt_same >1.)]
        ze_mask  = ze_same[(np.isnan(ze_same) == False) & (ppt_same >1.)]

        mask2 = np.ma.masked_array(ze_mask < 0.1)        
        #mask2 = np.ma.masked_array((ppt_mask < 20.) & (ze_mask > 50000))
 
        ppt_mask2_dummy    = ppt_mask[mask2 == False]
        ze_mask2_dummy     = ze_mask[mask2 == False]
        
        ppt_mask2    = ppt_mask2_dummy[ze_mask2_dummy >= 0.1]
        ze_mask2     = ze_mask2_dummy[ze_mask2_dummy >= 0.1]

        dict_result_macthes = {'ppt_matches':ppt_mask2 ,'ze_matches':ze_mask2}
        return dict_result_macthes
    
    def make_adjust(self, dict_result_macthes):

        self.ppt_mask2     = dict_result_macthes['ppt_matches'] 
        self.ze_mask2      = dict_result_macthes['ze_matches']
        self.ref_mask2     = 10.*np.log10(self.ze_mask2)

        self.log_pptmask2  = np.log10(self.ppt_mask2)
        self.log_zemask2   = np.log10(self.ze_mask2)
        self.dict_reg_orig = mytools.make_regresion(self.log_pptmask2, self.log_zemask2)
        self.B_orig        = self.dict_reg_orig['pendiente']
        self.A_orig        = 10. ** self.dict_reg_orig['intercepto']

        dict_res_bins = cal_m.adjust_by_bins(N_bins = 15, serie_x = self.log_pptmask2, serie_y = self.log_zemask2)
        self.medians_bins  = dict_res_bins['median']
        self.axisx_bins    = dict_res_bins['mean_pointx']
        self.dict_reg_bins = mytools.make_regresion(self.axisx_bins, self.medians_bins)
        self.B_bins        = self.dict_reg_bins['pendiente']
        self.A_bins        = 10. ** self.dict_reg_bins['intercepto']
    
    def return_corr_coefficients(self):
        corr_coef_orig = np.corrcoef(self.log_pptmask2, self.log_zemask2)
        corr_coef_bins = np.corrcoef(self.axisx_bins, self.medians_bins)
        dic_corr_coef  = {'corr_coef_orig':corr_coef_orig[0,1],'corr_coef_bins':corr_coef_bins[0,1]}
        return dic_corr_coef

    def return_adjust_coefficients(self): 
        dict_coefficients = {'B_bins': self.B_bins, 'A_bins':self.A_bins, 'B_orig':self.B_orig, 'A_orig':self.A_orig}
        return dict_coefficients
 
    def plot_ZR (self, type_plot, path_plot, name_plot_final, name_id, name_source):
        aux_array_ppt      = np.arange(0.0, 300.0, 0.001)
        aux_array_ref      = np.arange(-32.0, 90.0, 0.001)        
        # Adjust original data 
        log_adj_orig       = self.dict_reg_orig['pendiente']*np.log10(aux_array_ppt) +\
                             self.dict_reg_orig['intercepto']
        adj_orig           = ((10.**(aux_array_ref/10.))/self.A_orig)**(1/self.B_orig)
 
        log_str_morig      = str('%0.3f'%(self.dict_reg_orig['pendiente']))
        log_str_corig      = str('%0.3f'%(self.dict_reg_orig['intercepto']))
        str_Aorig          = str('%0.3f'%(self.A_orig))
        str_Borig          = str('%0.3f'%(self.B_orig))
        name_plot          = name_plot_final+'_'+name_id+'_'+name_source
       # Adjust with medians 
        log_adj_bins       = self.dict_reg_bins['pendiente']*np.log10(aux_array_ppt) +\
                             self.dict_reg_bins['intercepto']
        adj_bins           = ((10.**(aux_array_ref/10.))/self.A_bins)**(1/self.B_bins)

        log_str_mbins      = str('%0.3f'%(self.dict_reg_bins['pendiente']))
        log_str_cbins      = str('%0.3f'%(self.dict_reg_bins['intercepto']))
        str_Abins          = str('%0.3f'%(self.A_bins))
        str_Bbins          = str('%0.3f'%(self.B_bins))
        
        if (type_plot == 'Scatter'):
            plt.close()
            plt.cla()
            plt.clf()
            label_size = 8
            fig1 = plt.figure(1)
            fig1.set_figheight(8.0)
            fig1.set_figwidth(3.2)
            plt.subplots_adjust(left = 0.15,right = 0.95,top = 0.95, bottom = 0.1, hspace = 0.5, wspace = 0.3)

            ax1 = fig1.add_subplot(311)
            ax1.tick_params(axis='x', labelsize=label_size)
            ax1.tick_params(axis='y', labelsize=label_size)
            ax1.set_xlim(np.amin(self.ppt_mask2), np.amax(self.ppt_mask2))
            ax1.set_ylim(np.amin(self.ze_mask2), 50000.)
            ax1.set_xlabel(u'Rain Rate $[mm/h]$', fontsize = label_size)
            ax1.set_ylabel(u'Ze', fontsize = label_size)
            ax1.scatter(self.ppt_mask2, self.ze_mask2, marker = '.', s = 6, color = 'k', alpha = 0.6)
 
            plt.grid()
 
            ax2 = fig1.add_subplot(312)
            ax2.tick_params(axis='x', labelsize=label_size)
            ax2.tick_params(axis='y', labelsize=label_size)
            ax2.set_xlabel(u' $Log_{10}$(Rain Rate $[mm/h]$)', fontsize = label_size)
            ax2.set_ylabel(u'$Log_{10}$(Ze $[mm^6/m^3]$)', fontsize = label_size)
            ax2.set_xlim(np.amin(self.log_pptmask2)-0.01, np.amax(self.log_pptmask2))
            ax2.set_ylim(np.amin(self.log_zemask2), np.amax(self.log_zemask2))
            ax2.scatter(self.log_pptmask2, self.log_zemask2, marker = '.', s = 6, color = 'k', alpha = 0.4)
            ax2.scatter(self.axisx_bins, self.medians_bins, marker = 'o', s = 11, color = 'b', alpha = 1.0,\
                        label = 'Medians by intervals in X axis')
            ax2.plot(np.log10(aux_array_ppt), log_adj_orig, color = 'r', lw = 1.5,\
                        label = 'Least square regression with m ='+log_str_morig+' c='+log_str_corig)
            ax2.plot(np.log10(aux_array_ppt), log_adj_bins, color = 'b', lw = 1.3,\
                        label = 'Least square regression with m ='+log_str_mbins+' c='+log_str_cbins)
            plt.grid()
            plt.legend(loc=3, bbox_to_anchor=(0.0, -0.5,1.0,-0.3), fancybox=True, shadow=False,\
                        mode = 'expand' ,ncol=1, prop={'size':6})

            ax3 = fig1.add_subplot(313)    
            ax3.tick_params(axis='x', labelsize=label_size)
            ax3.tick_params(axis='y', labelsize=label_size)
            ax3.set_xlabel(u' Horizontal Reflectivity $[dBZ]$', fontsize = label_size)
            ax3.set_ylabel(u' Rain Rate $[mm/h]$', fontsize = label_size)
            ax3.set_xlim(np.amin(self.ref_mask2)-2., np.amax(self.ref_mask2) + 2.) 
            ax3.set_ylim(0.0, np.amax(self.ppt_mask2)+5.)
            ax3.scatter(self.ref_mask2, self.ppt_mask2, marker = '.', s = 6, color = 'k', alpha = 0.4)
            ax3.plot(aux_array_ref, adj_orig, color = 'r', lw = 1.5,\
                    label = 'ZR Relationship with A = '+str_Aorig+' B='+str_Borig)
            ax3.plot(aux_array_ref, adj_bins, color = 'b', lw = 1.5,\
                    label = 'ZR Relationship with A = '+str_Abins+' B='+str_Bbins)
            plt.grid()
            plt.legend(loc=3, bbox_to_anchor=(0.0, -0.45, 1.0,-0.25), fancybox=True, shadow=False,\
                        mode = 'expand' ,ncol=1, prop={'size':6})
       
            plt.savefig(path_plot+name_plot+'.pdf', format = 'pdf', dpi = 300 )

        if (type_plot == 'Contour_1'):           
            # Calculate neccesary values for plot cotours
            xedges1 = np.arange(-30,60,5)
            yedges1 = np.arange(-2,95,4)
            H, xedges, yedges = np.histogram2d(self.ppt_mask2, self.ref_mask2 ,bins = (yedges1, xedges1))
            mean_edge_ref = xedges[0:-1] + (xedges[1:] - xedges[0:-1])/2.
            mean_edge_ppt = yedges[0:-1] + (yedges[1:] - yedges[0:-1])/2.                         
            X, Y = np.meshgrid(mean_edge_ppt, mean_edge_ref)

            xedges1_log = np.arange(np.amin(self.log_pptmask2)-0.1, np.amax(self.log_pptmask2)+0.5,0.1)
            yedges1_log = np.arange(np.amin(self.log_zemask2)-0.2,np.amax(self.log_zemask2)+0.5,0.2)
            H_log, xedges_log, yedges_log = np.histogram2d(self.log_zemask2, self.log_pptmask2 ,\
                                            bins = (yedges1_log, xedges1_log))
            mean_edge_pptlog = xedges1_log[0:-1] + (xedges1_log[1:] - xedges1_log[0:-1])/2.
            mean_edge_zlog   = yedges1_log[0:-1] + (yedges1_log[1:] - yedges1_log[0:-1])/2.                                 
            X_log, Y_log = np.meshgrid(mean_edge_pptlog, mean_edge_zlog)

            color   = [(245, 245, 245), (210,210,210),(170, 170, 170),(136, 136, 136),\
                       (120,120,120),(104, 104, 104),(88,88,88),(72,72,72),(56,56,56),(40,40,40),\
                       (24, 24, 24)]
             
            my_colorbar = mytools.make_cmap(colors=color, bit=True)  
            #lev = [1.,10., 50.,100.,200.,300.,400.,500., 1000, 2000.]           
            lev = [10.,25.,100.,250.,500.,1000., 2500.,5000.,20000., 50000]
            norm = colors.BoundaryNorm(boundaries=lev, ncolors=256)
            
            plt.close()
            plt.cla()
            plt.clf()
            label_size = 8
            
            matplotlib.rcParams['axes.labelsize'] = label_size
 
            fig1 = plt.figure(1)
            fig1.set_figheight(5)
            fig1.set_figwidth(3.2)
            plt.subplots_adjust(left = 0.13,right = 0.95,top = 0.95, bottom = 0.1,hspace = 0.25, wspace = 0.1)

            ax1 = fig1.add_subplot(311)
            ax1.tick_params(axis='x', labelsize=label_size)
            ax1.tick_params(axis='y', labelsize=label_size)
            ax1.set_xlabel(u' $Log_{10}$(Rain Rate $[mm/h]$)', fontsize = label_size)
            ax1.set_ylabel(u'$Log_{10}$(Ze $[mm^6/m^3]$)', fontsize = label_size)
            ax1.set_xlim(np.amin(self.log_pptmask2)-0.01, np.amax(self.log_pptmask2))
            ax1.set_ylim(np.amin(self.log_zemask2), np.amax(self.log_zemask2))
            CS_log = ax1.contourf(X_log,Y_log,H_log, alpha=1, cmap = my_colorbar, norm = norm,\
                                  spacing = 'Uniform', levels = lev)
            ax1.contour(X_log,Y_log,H_log, colors = 'k', levels = lev, alpha = 0.3, lw = 0.5)
            ax1.scatter(self.axisx_bins, self.medians_bins, marker = 'o', s = 11, color = 'b', alpha = 1.0,\
                        label = 'Medians by intervals in X axis')
            #ax1.scatter(self.log_pptmask2, self.log_zemask2, marker = '.', s = 6, color = 'k', alpha = 0.4)
            ax1.plot(np.log10(aux_array_ppt), log_adj_orig, color = 'r', lw = 1.5,\
                        label = 'Least square regression with m ='+log_str_morig+' c='+log_str_corig)
            ax1.plot(np.log10(aux_array_ppt), log_adj_bins, color = 'b', lw = 1.3,\
                        label = 'Least square regression with m ='+log_str_mbins+' c='+log_str_cbins)
            plt.legend(loc=3, bbox_to_anchor=(0.0, -0.70,1.0,-0.55), fancybox=True, shadow=False,\
                        mode = 'expand' ,ncol=1, prop={'size':6}) 
 

            ax2 = fig1.add_subplot(212)
            ax2.tick_params(axis='x', labelsize=label_size)
            ax2.tick_params(axis='y', labelsize=label_size)
            ax2.set_xlabel(u' Horizontal Reflectivity $[dBZ]$', fontsize = label_size)
            ax2.set_ylabel(u' Rain Rate $[mm/h]$', fontsize = label_size)
 
            ax2.set_ylim(0,60)
            ax2.set_xlim(0,50)
            CS = ax2.contourf(X,Y,H, alpha=1, cmap = my_colorbar, norm = norm,\
                            spacing = 'uniform',levels = lev)
            ax2.contour(X,Y,H, colors = 'k', levels = lev, alpha = 0.3, lw = 0.5)
            ax2.plot(aux_array_ref, adj_orig, color = 'r', lw = 1.5,\
                    label = 'ZR Relationship with A = '+str_Aorig+' B='+str_Borig)
            ax2.plot(aux_array_ref, adj_bins, color = 'b', lw = 1.5,\
                    label = 'ZR Relationship with A = '+str_Abins+' B='+str_Bbins)
            plt.legend(loc=3, bbox_to_anchor=(0.0, -0.65, 1.0,-0.4), fancybox=True, shadow=False,\
                        mode = 'expand' ,ncol=1, prop={'size':6})
            cbar = plt.colorbar(CS, fraction=0.1, pad=0.35, orientation = 'horizontal', label = 'Total matches')
            #cbar.ax.set_axis_label_font(size = label_size)
            
            cbar.ax.tick_params(labelsize=label_size-2)
            cbar.ax.set_xticklabels(['10','25','100','250','500','1000','2500','5000','>20000 ', ' ']) 
            #cbar.ax.set_xticklabels(['1','10','50','100','200','300','400','500', '>1000', ' '])
            #ax2.scatter(self.ref_mask2, self.ppt_mask2, marker = '.', s = 6, color = 'k', alpha = 0.1)
            plt.savefig(path_plot+name_plot+'.pdf', format = 'pdf', dpi = 300 )

        if (type_plot == 'Contour_1_grays'):           
            # Calculate neccesary values for plot cotours
            xedges1 = np.arange(-30,60,5)
            yedges1 = np.arange(-2,95,4)
            H, xedges, yedges = np.histogram2d(self.ppt_mask2, self.ref_mask2 ,bins = (yedges1, xedges1))
            mean_edge_ref = xedges[0:-1] + (xedges[1:] - xedges[0:-1])/2.
            mean_edge_ppt = yedges[0:-1] + (yedges[1:] - yedges[0:-1])/2.                         
            X, Y = np.meshgrid(mean_edge_ppt, mean_edge_ref)
            xedges1_log = np.arange(np.amin(self.log_pptmask2)-0.1, np.amax(self.log_pptmask2)+0.5,0.1)
            yedges1_log = np.arange(np.amin(self.log_zemask2)-0.2,np.amax(self.log_zemask2)+0.5,0.2)
 
            H_log, xedges_log, yedges_log = np.histogram2d(self.log_zemask2, self.log_pptmask2 ,\
                                            bins = (yedges1_log, xedges1_log))
            mean_edge_pptlog = xedges1_log[0:-1] + (xedges1_log[1:] - xedges1_log[0:-1])/2.
            mean_edge_zlog   = yedges1_log[0:-1] + (yedges1_log[1:] - yedges1_log[0:-1])/2.                                 
            X_log, Y_log = np.meshgrid(mean_edge_pptlog, mean_edge_zlog)

            color   = [(245, 245, 245), (170, 170, 170),(136, 136, 136),\
                       (120,120,120),(104, 104, 104),(88,88,88),(72,72,72),(56,56,56),(40,40,40),\
                       (24, 24, 24)]
            
            my_colorbar = mytools.make_cmap(colors=color, bit=True)  
            lev = [1.,10., 50.,100.,200.,300.,400.,500., 1000, 2000.]           

            plt.close()
            plt.cla()
            plt.clf()
            label_size = 8
            
            matplotlib.rcParams['axes.labelsize'] = label_size
 
            fig1 = plt.figure(1)
            fig1.set_figheight(5)
            fig1.set_figwidth(3.2)
            plt.subplots_adjust(left = 0.13,right = 0.95,top = 0.95, bottom = 0.1,hspace = 0.25, wspace = 0.1)

            ax1 = fig1.add_subplot(311)
            ax1.tick_params(axis='x', labelsize=label_size)
            ax1.tick_params(axis='y', labelsize=label_size)
            ax1.set_xlabel(u' $Log_{10}$(Rain Rate $[mm/h]$)', fontsize = label_size)
            ax1.set_ylabel(u'$Log_{10}$(Ze $[mm^6/m^3]$)', fontsize = label_size)
            ax1.set_xlim(np.amin(self.log_pptmask2)-0.01, np.amax(self.log_pptmask2))
            ax1.set_ylim(np.amin(self.log_zemask2), np.amax(self.log_zemask2))
            CS_log = ax1.contourf(X_log,Y_log,H_log, alpha=1, cmap=my_colorbar, levels = lev)
            ax1.contour(X_log,Y_log,H_log, colors = 'k', levels = lev, alpha = 0.3, lw = 0.5)
            ax1.scatter(self.axisx_bins, self.medians_bins, marker = 'o', s = 11, color = 'b', alpha = 1.0,\
                        label = 'Medians by intervals in X axis')
            #ax1.scatter(self.log_pptmask2, self.log_zemask2, marker = '.', s = 6, color = 'k', alpha = 0.4)
            ax1.plot(np.log10(aux_array_ppt), log_adj_orig, color = 'r', lw = 1.5,\
                        label = 'Least square regression with m ='+log_str_morig+' c='+log_str_corig)
            ax1.plot(np.log10(aux_array_ppt), log_adj_bins, color = 'b', lw = 1.3,\
                        label = 'Least square regression with m ='+log_str_mbins+' c='+log_str_cbins)
            plt.legend(loc=3, bbox_to_anchor=(0.0, -0.70,1.0,-0.55), fancybox=True, shadow=False,\
                        mode = 'expand' ,ncol=1, prop={'size':6}) 
 

            ax2 = fig1.add_subplot(212)
            ax2.tick_params(axis='x', labelsize=label_size)
            ax2.tick_params(axis='y', labelsize=label_size)
            ax2.set_xlabel(u' Horizontal Reflectivity $[dBZ]$', fontsize = label_size)
            ax2.set_ylabel(u' Rain Rate $[mm/h]$', fontsize = label_size)
 
            ax2.set_ylim(0,60)
            ax2.set_xlim(0,50)
            CS = ax2.contourf(X,Y,H, alpha=1, cmap=my_colorbar, levels = lev)
            ax2.contour(X,Y,H, colors = 'k', levels = lev, alpha = 0.3, lw = 0.5)
            ax2.plot(aux_array_ref, adj_orig, color = 'r', lw = 1.5,\
                    label = 'ZR Relationship with A = '+str_Aorig+' B='+str_Borig)
            ax2.plot(aux_array_ref, adj_bins, color = 'b', lw = 1.5,\
                    label = 'ZR Relationship with A = '+str_Abins+' B='+str_Bbins)
            plt.legend(loc=3, bbox_to_anchor=(0.0, -0.65, 1.0,-0.4), fancybox=True, shadow=False,\
                        mode = 'expand' ,ncol=1, prop={'size':6})
            cbar = plt.colorbar(CS, fraction=0.1, pad=0.35, orientation = 'horizontal', label = 'Total matches')
            #cbar.ax.set_axis_label_font(size = label_size)
            
            cbar.ax.tick_params(labelsize=label_size-2)
            cbar.ax.set_xticklabels(['1','10','50','100','200','300','400','500', '>1000', ' '])
            #ax2.scatter(self.ref_mask2, self.ppt_mask2, marker = '.', s = 6, color = 'k', alpha = 0.1)
            plt.savefig(path_plot+name_plot+'.pdf', format = 'pdf', dpi = 300 )

        if (type_plot == 'Contour_2'):           
            # Calculate neccesary values for plot cotours
            xedges1 = np.arange(-30,60,5)
            yedges1 = np.arange(-2,95,4)
            H, xedges, yedges = np.histogram2d(self.ppt_mask2, self.ref_mask2 ,bins = (yedges1, xedges1))
            mean_edge_ref = xedges[0:-1] + (xedges[1:] - xedges[0:-1])/2.
            mean_edge_ppt = yedges[0:-1] + (yedges[1:] - yedges[0:-1])/2.                         
            X, Y = np.meshgrid(mean_edge_ppt, mean_edge_ref)

            color   = [(245, 245, 245), (170, 170, 170),(136, 136, 136),\
                       (120,120,120),(104, 104, 104),(88,88,88),(72,72,72),(56,56,56),(40,40,40),\
                       (24, 24, 24)]
            
            my_colorbar = mytools.make_cmap(colors=color, bit=True)  
            lev = [1.,10., 50.,100.,200.,300.,400.,500., 1000, 2000.]           

            plt.close()
            plt.cla()
            plt.clf()
            label_size = 8
            
            matplotlib.rcParams['axes.labelsize'] = label_size
 
            fig1 = plt.figure(1)
            fig1.set_figheight(4)
            fig1.set_figwidth(3.2)
            plt.subplots_adjust(left = 0.13,right = 0.95,top = 0.92, bottom = 0.2,hspace = 0.25, wspace = 0.1)

            ax1 = fig1.add_subplot(111)
            ax1.tick_params(axis='x', labelsize=label_size)
            ax1.tick_params(axis='y', labelsize=label_size)
            ax1.set_xlabel(u' Horizontal Reflectivity $[dBZ]$', fontsize = label_size)
            ax1.set_ylabel(u' Rain Rate $[mm/h]$', fontsize = label_size)
 
            ax1.set_ylim(0,60)
            ax1.set_xlim(0,50)
            CS = ax1.contourf(X,Y,H, alpha=1, cmap=my_colorbar, levels = lev)
            ax1.contour(X,Y,H, colors = 'k', levels = lev, alpha = 0.3, lw = 0.5)
            ax1.plot(aux_array_ref, adj_orig, color = 'r', lw = 1.5, \
                    label = 'ZR Relationship with A = '+str_Aorig+' B='+str_Borig)
            ax1.plot(aux_array_ref, adj_bins, color = 'b', lw = 1.5,\
                    label = 'ZR Relationship with A = '+str_Abins+' B='+str_Bbins)
            plt.legend(loc=3, bbox_to_anchor=(0.0, -0.55, 1.0,-0.30), fancybox=True, shadow=False,\
                        mode = 'expand' ,ncol=1, prop={'size':6})
            cbar = plt.colorbar(CS, fraction=0.1, pad=0.12, orientation = 'horizontal', label = 'Total matches')
            #cbar.ax.set_axis_label_font(size = label_size)
            
            cbar.ax.tick_params(labelsize=label_size-2)
            cbar.ax.set_xticklabels(['1','10','50','100','200','300','400','500', '>1000', ' '])
            #ax2.scatter(self.ref_mask2, self.ppt_mask2, marker = '.', s = 6, color = 'k', alpha = 0.1)
            plt.savefig(path_plot+name_plot+'.pdf', format = 'pdf', dpi = 300 )


        if (type_plot == 'Contour_2_grays'):           
            # Calculate neccesary values for plot cotours
            xedges1 = np.arange(-30,60,5)
            yedges1 = np.arange(-2,95,4)
            H, xedges, yedges = np.histogram2d(self.ppt_mask2, self.ref_mask2 ,bins = (yedges1, xedges1))
            mean_edge_ref = xedges[0:-1] + (xedges[1:] - xedges[0:-1])/2.
            mean_edge_ppt = yedges[0:-1] + (yedges[1:] - yedges[0:-1])/2.                         
            X, Y = np.meshgrid(mean_edge_ppt, mean_edge_ref)

            color   = [(245, 245, 245), (170, 170, 170),(136, 136, 136),\
                       (120,120,120),(104, 104, 104),(88,88,88),(72,72,72),(56,56,56),(40,40,40),\
                       (24, 24, 24)]
            
            my_colorbar = mytools.make_cmap(colors=color, bit=True)  
            lev = [1.,10., 50.,100.,200.,300.,400.,500., 1000, 2000.]           

            plt.close()
            plt.cla()
            plt.clf()
            label_size = 8
            
            matplotlib.rcParams['axes.labelsize'] = label_size
 
            fig1 = plt.figure(1)
            fig1.set_figheight(4)
            fig1.set_figwidth(3.2)
            plt.subplots_adjust(left = 0.13,right = 0.95,top = 0.92, bottom = 0.2,hspace = 0.25, wspace = 0.1)

            ax1 = fig1.add_subplot(111)
            ax1.tick_params(axis='x', labelsize=label_size)
            ax1.tick_params(axis='y', labelsize=label_size)
            ax1.set_xlabel(u' Horizontal Reflectivity $[dBZ]$', fontsize = label_size)
            ax1.set_ylabel(u' Rain Rate $[mm/h]$', fontsize = label_size)
 
            ax1.set_ylim(0,60)
            ax1.set_xlim(0,50)
            CS = ax1.contourf(X,Y,H, alpha=1, cmap=my_colorbar, levels = lev)
            ax1.contour(X,Y,H, colors = 'k', levels = lev, alpha = 0.3, lw = 0.5)
            ax1.plot(aux_array_ref, adj_orig, color = 'k', lw = 1.5, ls = ':', \
                    label = 'ZR Relationship with A = '+str_Aorig+' B='+str_Borig)
            ax1.plot(aux_array_ref, adj_bins, color = 'k', lw = 1.5,\
                    label = 'ZR Relationship with A = '+str_Abins+' B='+str_Bbins)
            plt.legend(loc=3, bbox_to_anchor=(0.0, -0.55, 1.0,-0.30), fancybox=True, shadow=False,\
                        mode = 'expand' ,ncol=1, prop={'size':6})
            cbar = plt.colorbar(CS, fraction=0.1, pad=0.12, orientation = 'horizontal', label = 'Total matches')
            #cbar.ax.set_axis_label_font(size = label_size)
            
            cbar.ax.tick_params(labelsize=label_size-2)
            cbar.ax.set_xticklabels(['1','10','50','100','200','300','400','500', '>1000', ' '])
            #ax2.scatter(self.ref_mask2, self.ppt_mask2, marker = '.', s = 6, color = 'k', alpha = 0.1)
            plt.savefig(path_plot+name_plot+'.pdf', format = 'pdf', dpi = 300 )
 
class zr_relation(object):

    def __init__(self, path_pkldata, name_stfiles, path_stations):
        self.path_pkldata    = path_pkldata
        self.name_stfiles    = name_stfiles
        self.path_stations   = path_stations

    # Source pude ser ALL, Disdrometro, SIATA_vaisala, SIATA, EPM
    def finder_station(self, source):
        self.source   = source
        self.stations = np.genfromtxt(self.path_stations + self.name_stfiles, delimiter = ',',\
            dtype =np.str)
        self.dummy_source = np.copy(np.array(self.stations[:, 1]))
        self.dummy_id     = np.copy(np.array(self.stations[:, 0]))
        if self.source == 'ALL':
            self.st_source = np.append(self.dummy_source[self.dummy_source == 'SIATA'],\
                                     self.dummy_source[self.dummy_source == 'SIATA_Vaisala'])
            self.st_source = np.append(self.st_source,self.dummy_source[self.dummy_source == 'Disdrometro'])
            self.st_id     = np.append(self.dummy_id[self.dummy_source == 'SIATA'],\
                                     self.dummy_id[self.dummy_source == 'SIATA_Vaisala'])
            self.st_id     = np.append(self.st_id, self.dummy_id[self.dummy_source == 'Disdrometro'])
        if self.source == 'SIATA':
            self.st_source = self.dummy_source[self.dummy_source == 'SIATA']
            self.st_id     = self.dummy_id[self.dummy_source == 'SIATA']
        if self.source == 'SIATA_Vaisala':
            self.st_source = self.dummy_source[self.dummy_source == 'SIATA_Vaisala']
            self.st_id     = self.dummy_id[self.dummy_source == 'SIATA_Vaisala']
        if self.source == 'Disdrometro':
            self.st_source = self.dummy_source[self.dummy_source == 'Disdrometro']
            self.st_id     = self.dummy_id[self.dummy_source == 'Disdrometro']
        if self.source == 'EPM':
            self.st_source = self.dummy_source[self.dummy_source == 'EPM']
            self.st_id   = self.dummy_id[self.dummy_source == 'EPM']
    def get_all (self, file_ext, resolution, how_res, type_figure, path_plot, name_plot_final):

        pos_dummy = range(len(self.st_id))
        #pos_dummy = [1]
        
        id_all         = np.array([])
        ppt_all        = np.array([])
        Ze_all         = np.array([])
        ccorr_org_all  = np.array([])
        ccorr_bin_all  = np.array([])
        Aorig_all      = np.array([]) 
        Borig_all      = np.array([])       
        Abin_all       = np.array([]) 
        Bbin_all       = np.array([]) 

        for ii in pos_dummy:
            self.source_element = self.st_source[ii]
            self.id_element     = self.st_id[ii]
            
            self.aux_name       = self.id_element+'_*'+file_ext
            self.aux_getdata    = plotter_zr(self.path_pkldata, self.aux_name,\
                                  self.source_element)
            self.aux_getdata.get_data()
            dict_res_matches    = self.aux_getdata.calculate_matches_with_time_resample(resolution = resolution,\
                                  how_res = how_res)
            self.aux_getdata.make_adjust(dict_res_matches)
            dic_corr_coef       = self.aux_getdata.return_corr_coefficients()
            #print dic_corr_coef
            dict_coefficients   = self.aux_getdata.return_adjust_coefficients()
            
            id_all         = np.append(id_all, self.id_element) 
            ppt_all        = np.append(ppt_all,dict_res_matches['ppt_matches']) 
            Ze_all         = np.append(Ze_all, dict_res_matches['ze_matches']) 
            ccorr_org_all  = np.append(ccorr_org_all, dic_corr_coef['corr_coef_orig']) 
            ccorr_bin_all  = np.append(ccorr_bin_all, dic_corr_coef['corr_coef_bins']) 
            Aorig_all      = np.append(Aorig_all, dict_coefficients['A_orig'])  
            Borig_all      = np.append(Borig_all, dict_coefficients['B_orig'])        
            Abin_all       = np.append(Abin_all, dict_coefficients['A_bins'])  
            Bbin_all       = np.append(Bbin_all, dict_coefficients['B_bins'])  


            if type_figure is not None:
                print 'Plot station: ', self.id_element,'__from', self.source_element, '-- resolution', resolution
                self.aux_getdata.plot_ZR(type_plot=type_figure,path_plot = path_plot,\
                                         name_plot_final=name_plot_final,\
                                         name_id = self.id_element, name_source = self.source_element)

        dict_all_data = {'id_all':id_all, 'ppt_all':ppt_all, 'Ze_all':Ze_all,'ccorr_org_all':ccorr_org_all ,\
                         'ccorr_bin_all':ccorr_bin_all,'Aorig_all':Aorig_all, 'Borig_all':Borig_all ,\
                         'Abin_all':Abin_all, 'Bbin_all':Bbin_all}
        return dict_all_data

