import dash
from dash import html, Input, Output, callback
import dash_bootstrap_components as dbc
from typing import List
from pathlib import Path
from urllib.parse import quote as urlquote
from app_config import APP_CONFIG
from calibre.library import CalibreLibrary


dash.register_page(__name__, path_template="/book/<calibre_id>")


def layout(calibre_id: str = 0, **kwargs):
    library = CalibreLibrary(APP_CONFIG.library_path)
    res = library.list(search=f"id:{calibre_id}")
    if len(res) == 0:
        return html.Div([html.P(f"No book with ID {calibre_id}")])
    elif len(res) > 1:
        return html.Div(
            [html.P(f"Error: Multiple books with ID {calibre_id} -> {res}")]
        )

    return html.Div(html.P(res[0].model_dump_json()))
    # extract_library_metadata()
