import json
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely.geometry import shape
from shapely.ops import unary_union
import random


# =========================
# GEOJSON → SHAPELY
# =========================
def geojson_to_shapely(data):
    return [shape(f["geometry"]) for f in data["features"]]


# =========================
# BUFFER
# =========================
def generate_buffer(geoms, dist=0.0001):
    return [g.buffer(dist) for g in geoms]


# =========================
# GRID SIMPLES
# =========================
def generate_grid(geom, size=0.0005):
    minx, miny, maxx, maxy = geom.bounds

    cells = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = shape({
                "type": "Polygon",
                "coordinates": [[
                    (x, y),
                    (x+size, y),
                    (x+size, y+size),
                    (x, y+size),
                    (x, y)
                ]]
            })
            if geom.intersects(cell):
                cells.append(cell)
            y += size
        x += size

    return cells


# =========================
# NDVI FAKE (mock)
# =========================
def add_ndvi_to_cells(cells):
    return [
        {"geometry": c, "ndvi": round(random.uniform(0.2, 0.9), 2)}
        for c in cells
    ]


# =========================
# VRA FAKE
# =========================
def add_vra_to_cells(cells):
    for c in cells:
        ndvi = c["ndvi"]
        c["dose"] = 100 if ndvi < 0.4 else 60 if ndvi < 0.7 else 30
    return cells


# =========================
# LINHAS (simples)
# =========================
def generate_planting_lines(geom, spacing=0.0003):
    minx, miny, maxx, maxy = geom.bounds

    lines = []
    x = minx
    while x < maxx:
        line = shape({
            "type": "LineString",
            "coordinates": [(x, miny), (x, maxy)]
        })
        if geom.intersects(line):
            lines.append(line)
        x += spacing

    return lines


# =========================
# STATS
# =========================
def compute_field_stats(cells):
    ndvis = [c["ndvi"] for c in cells]
    return {
        "ndvi_medio": sum(ndvis) / len(ndvis) if ndvis else 0
    }

# =========================
# LOAD GEOJSON
# =========================
def load_geojson(file):
    data = json.load(file)
    geoms = [shape(f["geometry"]) for f in data["features"]]
    return geoms


# =========================
# ÁREA (hectares)
# =========================
def calculate_area_hectares(geoms):
    union = unary_union(geoms)
    area_m2 = union.area  # ⚠️ isso ainda está em graus → vamos corrigir abaixo
    return area_m2


# =========================
# BUFFER (metros aproximado)
# =========================
def create_buffer(geoms, distance):
    buffered = [g.buffer(distance) for g in geoms]
    return buffered


# =========================
# CENTROIDE
# =========================
def get_centroid(geoms):
    union = unary_union(geoms)
    c = union.centroid
    return c.y, c.x


# =========================
# PARA GEOJSON
# =========================
def to_geojson(geoms):
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": mapping(g), "properties": {}}
            for g in geoms
        ],
    }
