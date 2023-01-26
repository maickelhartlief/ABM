from math import sqrt
# returns closest value of param that is within bounds
def set_valid(param, lower = 0, upper = 5, verbose = False, name = ''):
    '''
    description: returns closest value of param that is within bounds
    inputs:
        - param: desired parameter value
        - lower: optional, lower limit for the parameter
        - upper: optional, upper limit for the parameter
        - verbose: optional, whether to print if the desired value is invalid
        - name: optional, name of the parameter, for printing (only relevant if verbose)
    outputs:
        - closest valid parameter value
    '''
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


# normalized the distance to be inbetween .5 and 2, so that the max and min modifier is doubled or halfed.
def distance_normalizer(distance):
    return distance / sqrt(5**2 * 3 + 2**2) * 1.5 + .5
