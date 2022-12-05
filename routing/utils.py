def transform_km(float_km, if_m=False):
    '''
    Transforms a float distance value into km.

    Parameters:
    float_km: float to be transformed
    if_m: boolean switch, default is false. If float is distance in metre, set to True
    '''
    if if_m:
        str_km = f"{str(round(float_km/1000,2))} km"
        return str_km
    str_km = f"{str(round(float_km,2))} km"
    return str_km

def transform_min(float_min):
    '''
    Transforms float time variables into a format: 'x min y s'
    '''
    float_min_s = str(int(float(str(float_min).split('.')[1])/100*60))
    float_min_min = str(int(str(float_min).split('.')[0]))
    str_min = f'{float_min_min} min {float_min_s} s'
    return str_min
