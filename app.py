from dash import Dash, html, Input, Output
from calibre.calibre import extract_catalog
import dash_bootstrap_components as dbc
from pathlib import Path
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
from typing import List, Optional

server = Flask(__name__)
app = Dash(server=server, external_stylesheets=[dbc.themes.ZEPHYR])


@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(
        "/home/garvys/Documents/calibre-dashboard/assets/library",
        path,
        as_attachment=True,
    )


def file_download_link(formats: List[str]):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    p = Path(formats[0])
    p = p.relative_to("/home/garvys/Documents/calibre-dashboard/assets/library")

    location = "/download/{}".format(urlquote(str(p)))
    return html.A("Download", href=location)


def display_library(search: Optional[str] = None, row_size: int = 8):
    calibre_metadata = extract_catalog(
        "/home/garvys/Documents/calibre-dashboard/assets/library"
    )

    if search:
        calibre_metadata = [e for e in calibre_metadata if search.lower() in e.title.lower()]

    rows = [[]]

    for entry in calibre_metadata:
        cover_path = Path(entry.cover).relative_to(
            "/home/garvys/Documents/calibre-dashboard"
        )

        text = f""
        if entry.series:
            text += f"{entry.series}#{entry.series_index}"

        card = dbc.Card(
            [
                dbc.CardImg(src=str(cover_path), top=True),
                dbc.CardBody(
                    [
                        html.H6(entry.title, className="card-title"),
                        html.P(
                            entry.authors,
                            className="card-subtitle",
                        ),
                        html.P(text),
                        file_download_link(entry.formats),
                    ]
                ),
            ],
            className="p-2 m-2 rounded",
        )

        rows[-1].append(card)

        if len(rows[-1]) == row_size:
            rows.append([])

    rows = [row for row in rows if row]

    for row in rows:
        while len(row) < row_size:
            row.append(dbc.Card(className="p-2 m-2 invisible"))

    rows = [dbc.CardGroup(row) for row in rows]

    return rows


navbar = dbc.NavbarSimple(
    brand="Calibre Dashboard",
    children=[
        dbc.Input(id="input", placeholder="Type something...", type="text"),
        dbc.Button("Search", color="info")
        ],
    brand_href="#",
    color="primary",
    dark=True,
)


app.layout = html.Div([navbar, html.Div(children=display_library(), id="output")])

@app.callback(Output("output", "children"), [Input("input", "value")])
def output_text(value):
    print(value)
    return display_library(value)

if __name__ == "__main__":
    app.run(debug=True)
