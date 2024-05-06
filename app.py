from dash import Dash, html
from flask import Flask, send_from_directory
import dash_bootstrap_components as dbc
import dash
from app_config import APP_CONFIG

server = Flask(__name__)
app = Dash(server=server, use_pages=True, external_stylesheets=[dbc.themes.ZEPHYR])


@server.route("/download-from-library/<path:path>")
def download_from_library(path):
    return send_from_directory(
        APP_CONFIG.library_path,
        path,
        as_attachment=True,
    )


navbar = dbc.NavbarSimple(
    brand="Calibre Dashboard",
    # children=[
    #     dbc.Input(id="input", placeholder="Type something...", type="text"),
    #     dbc.Button("Search", color="info")
    #     ],
    brand_href="home",
    color="primary",
    dark=True,
)


app.layout = html.Div([navbar, dash.page_container])

if __name__ == "__main__":
    app.run(debug=APP_CONFIG.debug)
