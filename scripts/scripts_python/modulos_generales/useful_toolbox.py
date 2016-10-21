# -*- coding: utf-8 -*-
#!/usr/bin/env python
# ------------------------------------------------------------

import numpy as np
import pickle 


# 1- ========================== FUNCTION FOR OPEN PICKLE DATA=======================================
def open_pklfiles(path_pkldata):
    open_pkl = open(path_pkldata, 'rb')
    data = pickle.load(open_pkl)
    open_pkl.close()
    return data

# 2- ========================= FUNCTION FOR MAKE AN PKL DATA ======================================

def make_pickle(path_out, name_pkl, df_pkl):
    output_file = open(path_out+name_pkl+'.pkl', 'wb')
    pickle.dump(df_pkl, output_file)
    output_file.close()

# 3 - ======================== CALCULATE STATISTIC PARAMETERS =====================================

def calculate_cuantiles(cuantiles, array_in):
    aux_cuantiles = np.array([])
    for jj in cuantiles:
        #array_in = disdro_same 
        aux_mask = np.isnan(array_in)
        sort_array = np.sort(array_in[aux_mask == False])
        cuantil = sort_array[round(len(array_in[aux_mask == False])*jj/100.0)]
        aux_cuantiles = np.append(aux_cuantiles, cuantil)
    return aux_cuantiles

# 4 - ======================== Make linear regressions ============================================
def make_regresion(seriex, seriey):
    M_aux = np.vstack([seriex, np.ones(len(seriex))]).T
    m1, b1 = np.linalg.lstsq(M_aux, seriey)[0]
    dict_linealreg = {'pendiente':m1,'intercepto':b1}
    return dict_linealreg

def make_regresion_by_origin(seriex, seriey):
    m1 = np.sum(seriex*seriey)/np.sum(seriex**2)
    dict_linealreg = {'pendiente':m1,'intercepto':0}
    return dict_linealreg

# 5  - ===================== Meake a Color Bar  ==================================================

def make_cmap(colors, position=None, bit=False):
    '''
    make_cmap takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.
    Arrange your tuples so that the first color is the lowest value for the
    colorbar and the last is the highest.
    position contains values from 0 to 1 to dictate the location of each color.
    '''
    import matplotlib as mpl
    import numpy as np
    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)
    return cmap

def discrete_cmap_grayscale(N = 10):
    """create a colormap with N (N<15) discrete colors and register it"""
    # define individual colors as hex values
    cpool = ['#E8E8E8', '#D0D0D0','#B0B0B0','#A0A0A0','#989898','#888888',\
             '#707070', '#585858','#404040','#202020']
    cmap3 = col.ListedColormap(cpool[0:N], 'indexed')
    return cmap3

