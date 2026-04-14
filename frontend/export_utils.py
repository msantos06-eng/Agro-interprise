import json
from shapely.geometry import shape

def brand_package(name="AgroForce"):
    return {
        "app_name": name,
        "version": "1.0",
        "status": "active"
    }


def export_geojson(features):
    return json.dumps({
        "type": "FeatureCollection",
        "features": features
    }, ensure_ascii=False, indent=2)


def export_kml(features):
    import geopandas as gpd

    gdf = gpd.GeoDataFrame(
        features,
        geometry=[shape(f["geometry"]) for f in features],
        crs="EPSG:4326"
    )

    path = "/tmp/talhoes.kml"
    gdf.to_file(path, driver="KML")

    return path


def export_shapefile(features):
    import geopandas as gpd

    gdf = gpd.GeoDataFrame(
        features,
        geometry=[shape(f["geometry"]) for f in features],
        crs="EPSG:4326"
    )

    path = "/tmp/talhoes.shp"
    gdf.to_file(path)

    return path