#*******************************************************************************
# Calcula la intensidad de la lluvia utilizando reflectividad de radar 
# y las relaciones Z-R reportadas en la literatura
# Las ecuaciones son del tipo z=AR^B, donde A y B son constantes, z es 
# la reflectividad en mm6/m3 y es funcion de DBZH, DBZH=10log10(z)
# R es la intensidad en mm/hr
# La intensidad se calcula utilizando 8 expresiones diferentes:
# 0: 'Marshall-Palmer'
# 1: 'East cool stratiform'
# 2: 'West cool stratiform'
# 3: 'WSR-88D convective'
# 4: 'Rosenfeld convective'
# 5: 'Koistinnen-Michelson'
# 6: 'Joss et al'
# 7: 'Siata Disdrometro'
# 8: 'Ajuste_Est1'
# 9: 'Ajuste_Est2'
# 10: 'Ajuste_Est3'
# 11: 'Ajuste_Est4'
#*******************************************************************************

def rainRatesZR(Reflectividad, EQT):
    import numpy as np    
    DBZH = np.array(Reflectividad)
    
    zmm = 10**(DBZH/10.0)    
    A = np.array([200.0,130.0,75.0,300.0,250.0,200.0,500.0,269.129,59.36,30.94, 59.27,194.54])
    B = np.array([1.6,2.0,2.0,1.4,1.2,1.5,1.5,1.35, 0.94, 1.36, 1.15, 0.94,0.70])

    if (len(DBZH.shape) == 2):
        dim_f = DBZH.shape[0]
        dim_c = DBZH.shape[1]
        n_elements = dim_f*dim_c
        RR1 = np.array([-999.0]*n_elements, dtype = float)
        RR = np.reshape(RR1, (dim_f, dim_c))
        AA = np.reshape(RR1, (dim_f, dim_c))
        
    if (len(DBZH.shape) == 1):
        n_elements = len(DBZH)
        RR = np.array([-999.0]*n_elements, dtype = float)
        AA = np.array([-999.0]*n_elements, dtype = float)
    # Se hace el calculo de la  intensidad de precipitacion
    
    RR[DBZH != -999.0] = (zmm[DBZH != -999.0]/A[EQT])**(1/B[EQT])
    AA[DBZH != -999.0] = (1/4.0)*((zmm[DBZH != -999.0]/(A[EQT]))**(1/B[EQT])) 
    return RR, AA

