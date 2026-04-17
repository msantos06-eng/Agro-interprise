import folium
import numpy as np

def generate_map(ndvi):

    m = folium.Map(location=[-12.5, -45], zoom_start=6)

    folium.GeoJson(
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-46,-12], [-45,-12], [-45,-13], [-46,-13], [-46,-12]
                ]]
            }
        },
        name="Talhão"
    ).add_to(m)

    return m