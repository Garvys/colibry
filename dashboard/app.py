import dash
import dash_bootstrap_components as dbc
from app_config import APP_CONFIG
from calibre import CalibreLibrary
from dash import Dash, Input, Output, callback, dcc, html
from flask import Flask, send_from_directory

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
server = Flask(__name__)
app = Dash(
    server=server, use_pages=True, external_stylesheets=[dbc.themes.COSMO, dbc_css]
)


@server.route("/download-from-library/<path:path>")
def download_from_library(path):
    return send_from_directory(
        APP_CONFIG.library_path,
        path,
        as_attachment=True,
    )


navbar = dbc.NavbarSimple(
    brand="Colibry",
    children=[
        dbc.Button("Upload", color="primary", className="me-1"),
        dbc.Button("Reload Library", color="primary", id="reload-library"),
    ],
    brand_href="/home",
    color="primary",
    dark=True,
)


app.layout = html.Div([dcc.Store(id="library"), navbar, dash.page_container])


@callback(Output("library", "data"), Input("reload-library", "n_clicks"))
def load_library(_n_clicks):
    calibre_library = CalibreLibrary(APP_CONFIG.library_path)
    books_metadata = calibre_library.list()

    return [e.model_dump_json() for e in books_metadata]


if __name__ == "__main__":
    app.run(debug=APP_CONFIG.debug)
