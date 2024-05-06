import dash
from dash import html, Input, Output, callback
import dash_bootstrap_components as dbc
from typing import List
from pathlib import Path
from calibre.extract import extract_library_metadata
from urllib.parse import quote as urlquote
from app_config import APP_CONFIG
from calibre.filter import SearchFilters, filter_library_metadata


dash.register_page(__name__, path_template='/book/<calibre_id>')

def layout(calibre_id: str = 0, **kwargs):
    extract_library_metadata()
    return html.Div(
        [
            html.P()
        ]
    )
