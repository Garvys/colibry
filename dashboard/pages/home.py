import dash
from dash import html, Input, State, Output, callback, dcc
import dash_bootstrap_components as dbc
from typing import List, Optional
from pathlib import Path
from calibre.library import BookMetadata
from urllib.parse import quote as urlquote
from app_config import APP_CONFIG


dash.register_page(__name__)


def file_download_link(library_path: Path, formats: List[str]):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    p = Path(formats[0])
    p = p.relative_to(library_path)

    location = "/download-from-library/{}".format(urlquote(str(p)))
    return html.A(html.I(className="bi bi-download"), href=location)


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
                        html.H6(entry.title, className="card-title"),
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
            row.append(dbc.Card(className="p-2 m-2 rounded invisible"))

    rows = [dbc.CardGroup(row) for row in rows]

    if len(books_metadata) <= 1:
        t = f"{len(books_metadata)} e-book found :"
    else:
        t = f"{len(books_metadata)} e-books found :"

    res = html.Div([html.P(t, className="p-2"), html.Div(rows)])

    return res


def add_search():
    authors_dropdown = dbc.Col(
        [
            dbc.Label("Authors", html_for="autthors-filter"),
            dcc.Dropdown(
                id="authors-filter", multi=True, placeholder="Author", className="dbc"
            ),
        ],
        width=6,
    )
    series_dropdown = dbc.Col(
        [
            dbc.Label("Series", html_for="dropdown"),
            dcc.Dropdown(
                id="series-filter", multi=True, placeholder="Series", className="dbc"
            ),
        ],
        width=6,
    )
    authors_and_series = dbc.Row([authors_dropdown, series_dropdown])
    title_search = html.Div(
        [
            dbc.Label("Title"),
            dbc.Input(id="text-search", placeholder="Title", type="text"),
        ],
        className="mt-1",
    )
    sort_by_button = html.Div(
        [
            dbc.Label("Sort By:", html_for="sort-by"),
            dcc.Dropdown(
                value="Authors A->Z",
                options=["Authors A->Z", "Authors Z->A"],
                className="dbc",
                id="sort-by",
            ),
        ],
        className="mt-2",
    )
    search_button = html.Div(
        dbc.Button("Apply", color="primary", id="search-button"), className="mt-2"
    )
    return dbc.Form(
        [authors_and_series, title_search, sort_by_button, search_button],
        className="m-2",
    )


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H1("Home", className="m-2 pt-3 pb-3"),
                            add_search(),
                            html.Div(children=[], id="books-library"),
                        ]
                    ),
                    width={"size": 10, "offset": 1},
                ),
            ]
        )
    ]
)


@callback(
    Output("authors-filter", "options"),
    Input("library", "data"),
    prevent_initial_call=True,
)
def update_authors_list(library):
    books_metadata = [BookMetadata.model_validate_json(e) for e in library]

    authors = set(e.authors for e in books_metadata if e.authors)
    return sorted(list(authors))


@callback(
    Output("series-filter", "options"),
    Input("library", "data"),
    prevent_initial_call=True,
)
def update_series_list(library):
    books_metadata = [BookMetadata.model_validate_json(e) for e in library]

    authors = set(e.series for e in books_metadata if e.series)
    return sorted(list(authors))


@callback(
    Output("books-library", "children"),
    State("text-search", "value"),
    State("authors-filter", "value"),
    State("series-filter", "value"),
    State("sort-by", "value"),
    Input("library", "data"),
    Input("search-button", "n_clicks"),
)
def output_text(
    text_search: str,
    authors_filter: Optional[List[str]],
    series_filter: List[str],
    sort_by: str,
    library,
    _n_clicks,
):
    print(sort_by)
    books_metadata = [BookMetadata.model_validate_json(e) for e in library]
    if authors_filter:
        books_metadata = [b for b in books_metadata if b.authors in authors_filter]
    if series_filter:
        books_metadata = [b for b in books_metadata if b.series in series_filter]
    if text_search:
        books_metadata = [
            b for b in books_metadata if text_search.lower() in b.title.lower()
        ]
    if sort_by == "Authors A->Z":
        books_metadata = sorted(books_metadata, key=lambda x: x.authors)
    elif sort_by == "Authors Z->A":
        books_metadata = sorted(books_metadata, key=lambda x: x.authors, reverse=True)
    else:
        raise ValueError(f"Sort not supported: {sort_by}")
    print(len(library))
    return display_library(books_metadata)
