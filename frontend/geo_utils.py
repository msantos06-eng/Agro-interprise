from shapely.geometry import shape
import random

def geojson_to_shapely(geojson):
    return shape(geojson["geometry"] if "geometry" in geojson else geojson)

def generate_buffer(geom, dist):
    return geom.buffer(dist)

def generate_grid(geom):
    minx, miny, maxx, maxy = geom.bounds
    cells = []

    step = (maxx - minx) / 10

    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = shape({
                "type": "Polygon",
                "coordinates": [[
                    (x, y),
                    (x+step, y),
                    (x+step, y+step),
                    (x, y+step),
                    (x, y)
                ]]
            })
            if cell.intersects(geom):
                cells.append(cell)
            y += step
        x += step

    return cells

def add_ndvi_to_cells(cells):
    return [{"geometry": c, "ndvi": random.random()} for c in cells]

def add_vra_to_cells(cells):
    result = []
    for c in cells:
        dose = random.choice([60, 90, 120])
        result.append({"geometry": c, "dose": dose})
    return result

def generate_planting_lines(geom):
    return [geom]

def compute_field_stats(geom):
    return {
        "area_ha": round(geom.area * 100, 2),
        "perimeter_m": round(geom.length * 1000, 2)
    }