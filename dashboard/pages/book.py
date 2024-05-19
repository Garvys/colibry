import dash
from dash import html
from app_config import APP_CONFIG
from calibre.calibredb import CalibreDB


dash.register_page(__name__, path_template="/book/<calibre_id>")


def layout(calibre_id: str = 0, **kwargs):
    library = CalibreDB(APP_CONFIG.library_path)
    res = library.list(search=f"id:{calibre_id}")
    if len(res) == 0:
        return html.Div([html.P(f"No book with ID {calibre_id}")])
    elif len(res) > 1:
        return html.Div(
            [html.P(f"Error: Multiple books with ID {calibre_id} -> {res}")]
        )

    return html.Div(html.P(res[0].model_dump_json()))
    # extract_library_metadata()
