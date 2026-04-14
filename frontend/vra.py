import numpy as np

def generate_vra(ndvi):

    zones = np.zeros_like(ndvi)

    zones[ndvi < 0.3] = 1
    zones[(ndvi >= 0.3) & (ndvi < 0.6)] = 2
    zones[ndvi >= 0.6] = 3

    return zones