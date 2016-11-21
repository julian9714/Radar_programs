PRO test_datearray
make_datearray, 4, 1, 2016, 4, 30, 2016, fecha_inih, fecha_finh

stop
END

PRO make_datearray, mesini, dayini, yearini, mesfin, dayfin, yearfin, fecha_inih, fecha_finh
    all_dates = timegen(start = julday(mesini, dayini, yearini, 0, 0),$
        final = julday(mesfin, dayfin, yearfin, 23, 59), units = 'Hours')
    caldat, all_dates, monthh, dayh, yearh, hourh
    
    fecha_inih = strarr(n_elements(all_dates))
    fecha_finh = strarr(n_elements(all_dates))
    for ii= 0, n_elements(all_dates)-1, 1 do begin
        monthii = strtrim(monthh[ii],2) 
        dayii   = strtrim(dayh[ii],2)
        yearii  = strtrim(yearh[ii],2)
        hourii  = strtrim(hourh[ii],2)
        if strlen(monthii) eq 1 then monthii = '0'+monthii
        if strlen(dayii) eq 1 then dayii = '0'+dayii
        if strlen(hourii) eq 1 then hourii = '0'+hourii
        fini_dummy = yearii+'-'+monthii+'-'+dayii+' '+hourii+':00'
        ffin_dummy = yearii+'-'+monthii+'-'+dayii+' '+hourii+':59'
        fecha_inih[ii] = fini_dummy
        fecha_finh[ii] = ffin_dummy 
    endfor
END
