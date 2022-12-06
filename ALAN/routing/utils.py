
def transform_km(float_km):
    str_km = f"{str(round(float_km,2))} km"
    return str_km

def transform_min(float_min):
    float_min_s = str(int(float(str(float_min).split('.')[1])/100*60))
    float_min_min = str(int(str(float_min).split('.')[0]))
    str_min = f'{float_min_min} min {float_min_s} s'
    return str_min

def speed(walker_speed):
    if walker_speed == 'fast':
        return (7000)
    elif walker_speed == 'medium':
        return (4000)
    elif walker_speed == 'slow':
        return (3000)
