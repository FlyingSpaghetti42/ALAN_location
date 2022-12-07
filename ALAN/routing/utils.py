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

def transform_min(float_min, if_manhattan=False):
    '''
    Transforms float time variables into a format: 'x min y s'
    '''
    if if_manhattan:
        float_min = round(float_min, 2)
    float_min_s = str(int(float(str(float_min).split('.')[1])/100*60))
    float_min_min = str(int(str(float_min).split('.')[0]))
    str_min = f'{float_min_min} min {float_min_s} s'
    return str_min

def speed(walker_speed):
    if walker_speed == 'fast':
        return (7)
    elif walker_speed == 'medium':
        return (4)
    elif walker_speed == 'slow':
        return (3)
