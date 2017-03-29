# Este script contiene los modulos ncesarios para hacer QPE
# usando las variables polarietricas obtenidas del radar..
import numpy as np

class adjust_polars(object):
    def __init__(self, df_coincidentes):
        self.df_coincidentes = df_coincidentes

class plot_polarQPE(object):
    def __init__(self, dict_polar, pathout_plots, nameout_plots):
        self.dict_polar = dict_polar
        self.pathout_plots = pathout_plots
        self.nameout_plots = nameout_plots


class polar_QPE(object):

    def __init__(self, path_pkldata, name_stfiles, path_stations):
        # Esta clase es la que llama las clases:
        # --- Ajuste de las variables polares
        # --- Graficado de las variables.
        self.path_pkldata    = path_pkldata
        self.name_stfiles    = name_stfiles
        self.path_stations   = path_stations

    def finder_station(self, source):
        self.source   = source
        self.stations = np.genfromtxt(self.path_stations + self.name_stfiles, delimiter = ',',\
            dtype =np.str)
        self.dummy_source = np.copy(np.array(self.stations[:, 1]))
        self.dummy_id     = np.copy(np.array(self.stations[:, 0]))
        if self.source == 'ALL':
            self.st_source = np.append(self.dummy_source[self.dummy_source == 'SIATA'],\
                                       self.dummy_source[self.dummy_source == 'SIATA_Vaisala'])
            self.st_source = np.append(self.st_source,\
                                       self.dummy_source[self.dummy_source == 'Disdrometro'])
            self.st_id     = np.append(self.dummy_id[self.dummy_source == 'SIATA'],\
                                       self.dummy_id[self.dummy_source == 'SIATA_Vaisala'])
            self.st_id     = np.append(self.st_id,\
                                       self.dummy_id[self.dummy_source == 'Disdrometro'])
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
        return {'st_source':self.st_source , 'st_id':self.st_id}

    def get_all (self, file_ext, resolution, how_res, type_figure, path_plot, name_plot_final):

        pos_dummy = range(len(self.st_id))
        pos_dummy = [1]
        
        id_all         = np.array([])
        ppt_all        = np.array([])
        Zhe_all        = np.array([])
        Zve_all        = np.array([])
        Zdr_all        = np.array([])
        phi_dp         = np.array([])
        rho_hv         = np.array([])

        for ii in pos_dummy:
           self.source_element = self.st_source[ii]
           self.id_element     = self.st_id[ii]
           
           self.aux_name       = self.id_element+'_*'+file_ext
           self.aux_getdata    = plotter_zr(self.path_pkldata, self.aux_name,\
                                 self.source_element)
           self.aux_getdata.get_data()
           dict_res_matches    = self.aux_getdata.calculate_matches_with_time_resample(\
                                 resolution = resolution,\
                                 how_res = how_res)
           self.aux_getdata.make_adjust(dict_res_matches)
           dic_corr_coef       = self.aux_getdata.return_corr_coefficients()
           #print dic_corr_coef
           dict_coefficients   = self.aux_getdata.return_adjust_coefficients()
#            
#            id_all         = np.append(id_all, self.id_element) 
#            ppt_all        = np.append(ppt_all,dict_res_matches['ppt_matches']) 
#            Ze_all         = np.append(Ze_all, dict_res_matches['ze_matches']) 
#            ccorr_org_all  = np.append(ccorr_org_all, dic_corr_coef['corr_coef_orig']) 
#            ccorr_bin_all  = np.append(ccorr_bin_all, dic_corr_coef['corr_coef_bins']) 
#            Aorig_all      = np.append(Aorig_all, dict_coefficients['A_orig'])  
#            Borig_all      = np.append(Borig_all, dict_coefficients['B_orig'])        
#            Abin_all       = np.append(Abin_all, dict_coefficients['A_bins'])  
#            Bbin_all       = np.append(Bbin_all, dict_coefficients['B_bins'])  
#
#
#            if type_figure is not None:
#                print 'Plot station: ', self.id_element,'__from', self.source_element, '-- resolution', resolution
#                self.aux_getdata.plot_ZR(type_plot=type_figure,path_plot = path_plot,\
#                                         name_plot_final=name_plot_final,\
#                                         name_id = self.id_element, name_source = self.source_element)
#
#        dict_all_data = {'id_all':id_all, 'ppt_all':ppt_all, 'Ze_all':Ze_all,'ccorr_org_all':ccorr_org_all ,\
#                         'ccorr_bin_all':ccorr_bin_all,'Aorig_all':Aorig_all, 'Borig_all':Borig_all ,\
#                         'Abin_all':Abin_all, 'Bbin_all':Bbin_all}
#        return dict_all_data
#
