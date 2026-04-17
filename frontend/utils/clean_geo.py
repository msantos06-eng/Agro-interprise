def clean_geom(value):
    """
    Limpa valores para export (evita erro com numpy, None, etc)
    """
    try:
        if value is None:
            return None

        if hasattr(value, "item"):  # numpy
            return value.item()

        return value
    except:
        return None