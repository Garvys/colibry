import dash
from dash import html, Input, State, Output, callback, dcc
import dash_bootstrap_components as dbc
from typing import List
from pathlib import Path
from calibre.library import CalibreLibrary, BookMetadata
from urllib.parse import quote as urlquote
from app_config import APP_CONFIG
from pydantic import TypeAdapter
import json


dash.register_page(__name__)


def file_download_link(library_path: Path, formats: List[str]):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    p = Path(formats[0])
    p = p.relative_to(library_path)

    location = "/download-from-library/{}".format(urlquote(str(p)))
    return html.A("Download", href=location)


def display_library(books_metadata, row_size: int = 7):

    rows = [[]]

    for entry in books_metadata:
        cover_path = Path(entry.cover).relative_to(APP_CONFIG.library_path)

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
                            library_path=APP_CONFIG.library_path, formats=entry.formats
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
            row.append(dbc.Card(className="p-2 invisible"))

    rows = [dbc.CardGroup(row) for row in rows]

    res = html.Div(
        [
            html.P("32 E-books found.", className="p-2"),
            html.Div(rows)
        ]
    )

    return res

def add_search():
    authors_dropdown = dbc.Col(
        [
            dbc.Label("Authors", html_for="autthors-filter"),
            dcc.Dropdown(id="authors-filter", multi=True, placeholder="Author", className="dbc"),
        ], width=6
    )
    series_dropdown = dbc.Col(
        [
            dbc.Label("Series", html_for="dropdown"),
            dcc.Dropdown(id="series-filter", multi=True, placeholder="Series", className="dbc"),
        ],
        width=6
    )
    authors_and_series = dbc.Row([authors_dropdown, series_dropdown])
    title_search = html.Div(
        [
            dbc.Label("Title"),
            dbc.Input(id="text-search", placeholder="Title", type="text"),
        ], className="mt-1"
    )
    search_button = html.Div(dbc.Button("Apply", color="primary", id="search-button"), className="mt-2")
    return dbc.Form(
        [authors_and_series, title_search, search_button], className="m-2"
    )

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div(
                    [
                        html.H1("Home", className="m-2 pt-3 pb-3"),
                        add_search(),
                        html.Div(children=[], id="books-library"),
                    ]
                ), width={"size": 10, "offset": 1}),
            ]
        )
    ]
)

@callback(
      Output("authors-filter", "options"),
      Input("library", "data"),
      prevent_initial_call=True
)
def update_authors_list(library):
    books_metadata = [BookMetadata.model_validate_json(e) for e in library]

    authors = set(e.authors for e in books_metadata if e.authors)
    return sorted(list(authors))

@callback(
      Output("series-filter", "options"),
      Input("library", "data"),
      prevent_initial_call=True
)
def update_series_list(library):
    books_metadata = [BookMetadata.model_validate_json(e) for e in library]

    authors = set(e.series for e in books_metadata if e.series)
    return sorted(list(authors))



@callback(
    Output("books-library", "children"),
    State("text-search", "value"),
    Input("library", "data"),
    Input("search-button", "n_clicks"),
)
def output_text(text_search: str, library, _n_clicks):
    books_metadata = [BookMetadata.model_validate_json(e) for e in library]
    print(len(library))
    return display_library(books_metadata)
