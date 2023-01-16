def set_valid(param, lower = 0, upper = 5, verbose = False, name = ''):
    valid = True
    out = param

    if param < lower:
        valid = False
        out = lower
    elif param > upper:
        valid = False
        out = upper
    
    if verbose and not valid:
        print(f'invalid value for {name}: {param}. set to {out}')
    return out