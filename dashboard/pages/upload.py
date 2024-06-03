import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path_template="/upload")


def layout(**kwargs):
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1("Upload Ebook", className="mt-4 mb-4"),
                            dcc.Upload(
                                id="upload-data",
                                children=html.Div(
                                    ["Drag and Drop or ", html.A("Select Files")]
                                ),
                                style={
                                    "width": "100%",
                                    "height": "60px",
                                    "lineHeight": "60px",
                                    "borderWidth": "1px",
                                    "borderStyle": "dashed",
                                    "borderRadius": "5px",
                                    "textAlign": "center",
                                    "margin": "10px",
                                },
                                # Allow multiple files to be uploaded
                                multiple=True,
                            ),
                            html.Div(id="output-data-upload"),
                        ],
                        width={"size": 10, "offset": 1},
                    )
                ]
            ),
        ]
    )
