import dash
from dash import html, Input, Output, callback
import dash_bootstrap_components as dbc
from typing import List
from pathlib import Path
from urllib.parse import quote as urlquote
from app_config import APP_CONFIG


dash.register_page(__name__, path_template="/book/<calibre_id>")


def layout(calibre_id: str = 0, **kwargs):
    # extract_library_metadata()
    return html.Div([html.P()])
