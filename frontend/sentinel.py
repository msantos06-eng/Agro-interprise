import requests

import streamlit as st
import folium
from folium.plugins import Draw, MeasureControl, LocateControl, Geocoder
from streamlit_folium import st_folium
import json
import numpy as np
import pandas as pd
from shapely.geometry import mapping

from geo_utils import (
    geojson_to_shapely, generate_buffer, generate_grid,
    add_ndvi_to_cells, add_vra_to_cells, generate_planting_lines,
    compute_field_stats,
)
from utils.export_utils import export_geojson

from utils.clean_geo import clean_geom

def get_token(client_id, client_secret):

    url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

    data = {
        "grant_type": "client_credentials",
        "sh-c0dac085-be43-4a1a-846b-9f2007c39719": client_id,
        "mquL3Z5gSzNGH8Dq4eAynUuczrC7P5UE": client_secret
    }

    r = requests.post(url, data=data)
    return r.json()["access_token"]