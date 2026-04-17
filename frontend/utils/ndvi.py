import random
from shapely.geometry import box


def generate_grid(geom, cell_size):
    """
    Gera uma grade quadrada dentro do talhão
    """
    minx, miny, maxx, maxy = geom.bounds

    cells = []
    cell_id = 0

    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = box(x, y, x + cell_size, y + cell_size)

            if cell.intersects(geom):
                clipped = cell.intersection(geom)

                area_ha = clipped.area / 10000

                cells.append({
                    "cell_id": cell_id,
                    "geometry_wgs84": clipped,
                    "area_ha": area_ha
                })

                cell_id += 1

            y += cell_size
        x += cell_size

    return cells


def add_ndvi_to_cells(cells):
    """
    Simula NDVI (0 a 1)
    """
    for c in cells:
        c["ndvi"] = round(random.uniform(0.2, 0.9), 3)

    return cells