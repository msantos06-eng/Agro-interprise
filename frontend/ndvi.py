import numpy as np

def calculate_ndvi(red, nir):
    return (nir - red) / (nir + red + 1e-10)