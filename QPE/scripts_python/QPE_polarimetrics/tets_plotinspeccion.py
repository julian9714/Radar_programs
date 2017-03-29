# Esta parte de codigo es la que se usa para hacer un
# paneo rapido del comportamiento de las variables polares con 
# respecto a la reflectividad y la precipitacion.

# Hacemos las graficas exploratorias de las variables 

label_size = 9
plt.close()
plt.cla()
plt.clf()

fig1 = plt.figure(1)
fig1.set_figheight(8.0)
fig1.set_figwidth(12.0)

plt.subplots_adjust(left = 0.08,right = 0.95,top = 0.95, bottom = 0.08, hspace = 0.5, wspace = 0.3)
# Primera fila de la grafica.
ax11 = fig1.add_subplot(351)
ax11.tick_params(axis='y', labelsize=label_size)
ax11.tick_params(axis='x', labelsize=label_size)
ax11.set_ylabel(u'dBZ Disdrometer', fontsize = label_size)
ax11.set_ylim(-9.9, 60.0)
ax11.set_xlim(-32.0, 60.0)
ax11.scatter(dbzh_arr, dbzdisd_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

ax12 = fig1.add_subplot(352)
ax12.tick_params(axis='y', labelsize=label_size)
ax12.tick_params(axis='x', labelsize=label_size)
ax12.set_ylim(-9.9, 60.0)
ax12.set_xlim(-32.0, 60.0)
ax12.scatter(dbzv_arr, dbzdisd_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

ax13 = fig1.add_subplot(353)
ax13.tick_params(axis='y', labelsize=label_size)
ax13.tick_params(axis='x', labelsize=label_size)
ax13.set_ylim(-9.9, 60.0)
ax13.set_xlim(-10.0, 10.0)
ax13.scatter(zdr_arr, dbzdisd_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

ax14 = fig1.add_subplot(354)
ax14.tick_params(axis='y', labelsize=label_size)
ax14.tick_params(axis='x', labelsize=label_size)
ax14.set_ylim(-9.9, 60.0)
ax14.set_xlim(-200., 200.)
ax14.scatter(phidp_arr, dbzdisd_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

ax15 = fig1.add_subplot(355)
ax15.tick_params(axis='y', labelsize=label_size)
ax15.tick_params(axis='x', labelsize=label_size)
ax15.set_ylim(-9.9, 80.0)
ax15.set_xlim(0.0, 1.0)
ax15.scatter(rhohv_arr, dbzdisd_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

# Segunda fila
ax21 = fig1.add_subplot(356)
ax21.tick_params(axis='y', labelsize=label_size)
ax21.tick_params(axis='x', labelsize=label_size)
ax21.set_ylabel(u'dBZ Disdrometer', fontsize = label_size)
ax21.set_ylim(0.0, 60.0)
ax21.set_xlim(-32.0, 60.0)
ax21.scatter(dbzh_arr[pptalld_arr > 0], pptalld_arr[pptalld_arr > 0],\
             marker = '.', s = 6, color = 'k', alpha = 0.8)

ax22 = fig1.add_subplot(357)
ax22.tick_params(axis='y', labelsize=label_size)
ax22.tick_params(axis='x', labelsize=label_size)
ax22.set_ylim(-9.9, 60.0)
ax22.set_xlim(-32.0, 60.0)
ax22.scatter(dbzv_arr[pptalld_arr > 0], pptalld_arr[pptalld_arr > 0],\
             marker = '.', s = 6, color = 'k', alpha = 0.8)

ax23 = fig1.add_subplot(358)
ax23.tick_params(axis='y', labelsize=label_size)
ax23.tick_params(axis='x', labelsize=label_size)
ax23.set_ylim(-9.9, 60.0)
ax23.set_xlim(-10.0, 10.0)
ax23.scatter(zdr_arr[pptalld_arr > 0], pptalld_arr[pptalld_arr > 0],\
             marker = '.', s = 6, color = 'k', alpha = 0.8)

ax24 = fig1.add_subplot(359)
ax24.tick_params(axis='y', labelsize=label_size)
ax24.tick_params(axis='x', labelsize=label_size)
ax24.set_ylim(-9.9, 60.0)
ax24.set_xlim(-200., 200.)
ax24.scatter(phidp_arr[pptalld_arr > 0], pptalld_arr[pptalld_arr > 0],
             marker = '.', s = 6, color = 'k', alpha = 0.8)

ax25 = fig1.add_subplot(3,5,10)
ax25.tick_params(axis='y', labelsize=label_size)
ax25.tick_params(axis='x', labelsize=label_size)
ax25.set_ylim(-9.9, 80.0)
ax25.set_xlim(0.0, 1.0)
ax25.scatter(rhohv_arr[pptalld_arr > 0], pptalld_arr[pptalld_arr > 0],\
             marker = '.', s = 6, color = 'k', alpha = 0.8)

# Tercera fila
ax31 = fig1.add_subplot(3,5,11)
ax31.tick_params(axis='y', labelsize=label_size)
ax31.tick_params(axis='x', labelsize=label_size)
ax31.set_ylabel(u'dBZ Disdrometer', fontsize = label_size)
ax31.set_ylim(-9.9, 60.0)
ax31.set_xlim(-32.0, 60.0)
ax31.scatter(dbzh_arr, pptintm_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

ax32 = fig1.add_subplot(3,5,12)
ax32.tick_params(axis='y', labelsize=label_size)
ax32.tick_params(axis='x', labelsize=label_size)
ax32.set_ylim(-9.9, 60.0)
ax32.set_xlim(-32.0, 60.0)
ax32.scatter(dbzv_arr, pptintm_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

ax33 = fig1.add_subplot(3,5,13)
ax33.tick_params(axis='y', labelsize=label_size)
ax33.tick_params(axis='x', labelsize=label_size)
ax33.set_ylim(-9.9, 60.0)
ax33.set_xlim(-10.0, 10.0)
ax33.scatter(zdr_arr, pptintm_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

ax34 = fig1.add_subplot(3,5,14)
ax34.tick_params(axis='y', labelsize=label_size)
ax34.tick_params(axis='x', labelsize=label_size)
ax34.set_ylim(-9.9, 60.0)
ax34.set_xlim(-200., 200.)
ax34.scatter(phidp_arr, pptintm_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

ax35 = fig1.add_subplot(3,5,15)
ax35.tick_params(axis='y', labelsize=label_size)
ax35.tick_params(axis='x', labelsize=label_size)
ax35.set_ylim(-9.9, 80.0)
ax35.set_xlim(0.0, 1.0)
ax35.scatter(rhohv_arr, pptintm_arr, marker = '.', s = 6, color = 'k', alpha = 0.8)

plt.savefig('test.png', format = 'png')

