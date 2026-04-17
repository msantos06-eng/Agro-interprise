import io
import zipfile
import json
from shapely.geometry import mapping
import numpy as np

from .clean_geo import clean_geom


PRJ_WGS84 = ('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
              'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
              'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')


class _GeoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super().default(obj)

    def encode(self, obj):
        return super().encode(self._convert(obj))

    def _convert(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, dict):
            return {k: self._convert(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._convert(i) for i in obj]
        return obj


def _geom_dict(geom):
    raw = mapping(geom)

    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [clean(i) for i in obj]
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return obj

    return clean(raw)


def export_geojson(features, geometry_key='geometry_wgs84', properties=None):
    features_list = []

    for feat in features:
        geom = feat.get(geometry_key)

        if geom is None or geom.is_empty:
            continue

        keys = properties if properties is not None else [
            k for k in feat if k not in ('geometry_wgs84', 'geometry_utm')
        ]

        props = {k: clean_geom(feat.get(k)) for k in keys}

        features_list.append({
            "type": "Feature",
            "geometry": clean_geom(mapping(geom)),
            "properties": props
        })

    return json.dumps(
        {"type": "FeatureCollection", "features": features_list},
        ensure_ascii=False,
        indent=2
    )


def brand_package_multi(talhoes, brand):
    field_geom = None
    cells = []
    lines = []
    buffer_geom = None

    for t in talhoes:
        if t.get("geom"):
            field_geom = t["geom"]

        if t.get("grid_cells"):
            cells.extend(t["grid_cells"])

        if t.get("lines"):
            lines.extend(t["lines"])

        if t.get("buffer_geom"):
            buffer_geom = t["buffer_geom"]

    return brand_package(field_geom, cells, lines, buffer_geom, brand)


def export_shapefile_zip(features, geometry_key='geometry_wgs84', properties=None, name='export'):
    try:
        import shapefile
    except ImportError:
        return None

    if not features:
        return None

    sample_geom = features[0].get(geometry_key)
    if sample_geom is None:
        return None

    buf_shp = io.BytesIO()
    buf_shx = io.BytesIO()
    buf_dbf = io.BytesIO()
    w = shapefile.Writer(shp=buf_shp, shx=buf_shx, dbf=buf_dbf)

    geom_type = sample_geom.geom_type
    if 'Polygon' in geom_type:
        w.shapeType = shapefile.POLYGON
    elif 'Line' in geom_type:
        w.shapeType = shapefile.POLYLINE
    else:
        w.shapeType = shapefile.POINT

    if properties is None:
        properties = [k for k in features[0] if k not in ('geometry_wgs84', 'geometry_utm')]

    for prop in properties:
        val = features[0].get(prop, '')
        if isinstance(val, (int, np.integer)):
            w.field(prop[:10], 'N', 10, 0)
        elif isinstance(val, (float, np.floating)):
            w.field(prop[:10], 'F', 15, 4)
        else:
            w.field(prop[:10], 'C', 50)

    for feat in features:
        geom = feat.get(geometry_key)
        if geom is None or geom.is_empty:
            continue

        geom_dict = _geom_dict(geom)
        gt = geom_dict['type']
        coords = geom_dict['coordinates']

        try:
            if 'Polygon' in gt:
                if gt == 'Polygon':
                    w.poly([list(r) for r in coords])
                else:
                    w.poly([list(r) for poly in coords for r in poly])
            elif 'LineString' in gt:
                if gt == 'LineString':
                    w.line([list(coords)])
                else:
                    w.line([list(part) for part in coords])
        except Exception:
            continue

        record = []
        for prop in properties:
            val = feat.get(prop, '')
            if isinstance(val, np.integer):
                val = int(val)
            elif isinstance(val, np.floating):
                val = float(val)
            record.append(val)

        w.record(*record)

    w.close()

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f'{name}.shp', buf_shp.getvalue())
        zf.writestr(f'{name}.shx', buf_shx.getvalue())
        zf.writestr(f'{name}.dbf', buf_dbf.getvalue())
        zf.writestr(f'{name}.prj', PRJ_WGS84)

    return zip_buf.getvalue()


def brand_readme(brand):
    return f"Exportação gerada para {brand}\nSistema: AgroForce\n"


# ✅ ÚNICA FUNÇÃO (SEM DUPLICAÇÃO E COM RETURN)
def brand_package(field_geom, cells, lines, buffer_geom, brand):
    files = {}

    if field_geom:
        feats = [{'geometry_wgs84': field_geom}]
        files['talhao.geojson'] = export_geojson(feats, properties=[]).encode()
        shp = export_shapefile_zip(feats, properties=[], name='talhao')
        if shp:
            files['talhao_shp.zip'] = shp

    if cells:
        props = ['cell_id', 'area_ha', 'ndvi', 'classe']
        if cells and 'dose' in cells[0]:
            props += ['dose', 'produto']

        files['prescricao.geojson'] = export_geojson(cells, properties=props).encode()
        shp = export_shapefile_zip(cells, properties=props, name='prescricao')
        if shp:
            files['prescricao_shp.zip'] = shp

    if lines:
        props_l = ['line_id', 'comprimento_m']
        files['linhas_plantio.geojson'] = export_geojson(lines, properties=props_l).encode()
        shp = export_shapefile_zip(lines, properties=props_l, name='linhas_plantio')
        if shp:
            files['linhas_plantio_shp.zip'] = shp

    if buffer_geom:
        feats = [{'geometry_wgs84': buffer_geom}]
        files['buffer.geojson'] = export_geojson(feats, properties=[]).encode()

    files['LEIA-ME.txt'] = brand_readme(brand).encode()

    final_zip = io.BytesIO()
    with zipfile.ZipFile(final_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname, content in files.items():
            zf.writestr(f'{brand}/{fname}', content)

    final_zip.seek(0)
    return final_zip.getvalue()