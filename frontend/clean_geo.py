import numpy as np

def clean_geom(obj):
    if isinstance(obj, dict):
        return {k: clean_geom(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_geom(i) for i in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    return obj