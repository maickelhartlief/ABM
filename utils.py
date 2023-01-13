def set_valid(name, param, min = 0, max = 4, default = 0):
    if not (min <= param <= max):
        print(f'invalid value for {name}: {param}. set to {default}')
        param = default
    return param
