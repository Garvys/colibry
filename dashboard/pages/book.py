import dash
from dash import html, callback, dash_table
from app_config import APP_CONFIG
from calibre import CalibreSql, CalibreField, BookMetadata, SearchParams, EqualityFilter
from pathlib import Path
import dash_bootstrap_components as dbc
from urllib.parse import quote as urlquote
from core.download import ebook_download_link


dash.register_page(__name__, path_template="/book/<book_id>")


def generate_table(book: BookMetadata) -> dbc.Table:
    data = [
        ("id", book.id, False),
        ("title", book.title, True),
        ("authors", book.authors, True),
        ("series", book.series, True),
        ("series_index", book.series_index, True),
        ("timestamp", book.timestamp, False),
    ]
    trs = []
    for e in data:
        edit_button = html.Div([])
        if e[2]:
            edit_button = dbc.Button(
                html.I(className="bi bi-pencil"),
                className="ms-2",
                color="light",
                size="sm",
                style={"backgroundColor": "#ffffff", "borderColor": "#ffffff"},
            )
        trs.append(
            html.Tr(
                [
                    html.Td(children=e[0]),
                    html.Td(children=[e[1], edit_button]),
                ]
            )
        )
    return dbc.Table(html.Tbody(trs), bordered=True, hover=True, responsive=True)


def layout(book_id: str = 0, **kwargs):
    lib = CalibreSql(APP_CONFIG.library_path)
    books = lib.list_books(
        params=SearchParams(
            fields=[
                CalibreField.cover,
                CalibreField.authors,
                CalibreField.series,
                CalibreField.series_index,
                CalibreField.timestamp,
                CalibreField.formats,
            ],
            filters=[EqualityFilter.with_id(book_id)],
        )
    )

    # TODO: Add error check
    book = books[0]

    cover_path = Path(book.cover).relative_to(APP_CONFIG.library_path)

    return html.Div(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1(book.title, className="mt-4 mb-4"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(
                                        src=f"/download-from-library/{urlquote(str(cover_path))}",
                                        className="img-responsive rounded ebook-cover",
                                        style={"maxWidth": "100%"},
                                    ),
                                    className="col-md-4",
                                ),
                                dbc.Col(
                                    [
                                        html.H4("Metadata"),
                                        generate_table(book),
                                        dbc.Button(
                                            "Download Ebook",
                                            href=ebook_download_link(
                                                "",
                                                library_path=APP_CONFIG.library_path,
                                                ebook_path=book.formats[0],
                                            ),
                                            external_link=True,
                                        ),
                                    ],
                                    className="col-md-8",
                                ),
                            ]
                        ),
                    ],
                    width={"size": 10, "offset": 1},
                )
            )
        ],
        className="m-2",
    )
    # extract_library_metadata()
