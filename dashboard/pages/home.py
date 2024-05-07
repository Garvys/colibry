import dash
from dash import html, Input, State, Output, callback, dcc
import dash_bootstrap_components as dbc
from typing import List
from pathlib import Path
from calibre.library import CalibreLibrary
from urllib.parse import quote as urlquote
from app_config import APP_CONFIG


dash.register_page(__name__)


def file_download_link(library_path: Path, formats: List[str]):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    p = Path(formats[0])
    p = p.relative_to(library_path)

    location = "/download-from-library/{}".format(urlquote(str(p)))
    return html.A("Download", href=location)


def display_library(library_path: Path, search: str = "", row_size: int = 8):
    calibre_library = CalibreLibrary(APP_CONFIG.library_path)
    books_metadata = calibre_library.list(search=search)

    rows = [[]]

    for entry in books_metadata:
        cover_path = Path(entry.cover).relative_to(library_path)

        text = ""
        if entry.series:
            text += f"{entry.series}#{entry.series_index}"

        card = dbc.Card(
            [
                dbc.CardImg(
                    src=f"/download-from-library/{urlquote(str(cover_path))}", top=True
                ),
                dbc.CardBody(
                    [
                        dcc.Link(
                            html.H6(entry.title, className="card-title"),
                            href=f"/book/{entry.id}",
                        ),
                        html.P(
                            entry.authors,
                            className="card-subtitle",
                        ),
                        html.P(text),
                        file_download_link(
                            library_path=library_path, formats=entry.formats
                        ),
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


layout = html.Div(
    [
        dbc.Input(id="text-search", placeholder="Type something...", type="text"),
        dbc.Button("Search", color="info", id="search-button"),
        html.Div(children=[], id="books-library"),
    ]
)


@callback(
    Output("books-library", "children"),
    State("text-search", "value"),
    Input("search-button", "n_clicks"),
)
def output_text(text_search: str, _n_clicks):
    return display_library(library_path=APP_CONFIG.library_path, search=text_search)
