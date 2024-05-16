import dash
import dash_bootstrap_components as dbc
from app_config import APP_CONFIG
from calibre import CalibreLibrary
from dash import Dash, Input, Output, callback, dcc, html, State
from flask import Flask, send_from_directory

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
server = Flask(__name__)
app = Dash(
    server=server,
    use_pages=True,
    external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP, dbc_css],
)


@server.route("/download-from-library/<path:path>")
def download_from_library(path):
    return send_from_directory(
        APP_CONFIG.library_path,
        path,
        as_attachment=True,
    )


navbar_right = dbc.Nav(
    [
        # dbc.Col(dbc.Input(type="search", placeholder="Search")),
        # dbc.Col(
        #     dbc.Button(
        #         "Search", color="primary", className="ms-2", n_clicks=0
        #     ),
        #     width="auto",
        # ),
        dbc.Button(html.I(className="bi bi-upload", id="upload-button")),
        dbc.Button(
            html.I(
                className="bi bi-bootstrap-reboot",
                id="reload-library",
            ),
            class_name="ms-1",
        ),
        # dbc.NavItem(
        #     dbc.NavLink(
        #         html.I(
        #             className="bi bi-upload", id="upload-button"
        #         )
        #     )
        # ),
        # dbc.NavItem(
        #     dbc.NavLink(
        #         html.I(
        #             className="bi bi-bootstrap-reboot",
        #             id="reload-library",
        #         )
        # )),
        dbc.Tooltip(
            "Upload a new book to the lilbrary.",
            target="upload-button",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Re-index the Calibre Library. Necessary if some changes have been performed to the library.",
            target="reload-library",
            placement="bottom",
        ),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    # align="center",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    # dbc.Col(
                    #     dcc.Link(
                    #         html.Img(src="assets/logo.jpg", height="40px"), href="/home"
                    #     )
                    # ),
                    dbc.Col(
                        dbc.NavbarBrand(
                            html.Img(src="assets/Colibry.svg", height="40px"),
                            href="/home",
                        ),
                        align="center",
                        className="g-0",
                    ),
                ]
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                navbar_right,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
            #     dbc.Col(
            #         dbc.Nav(
            #             [
            #                 dbc.NavItem(
            #                     dbc.NavLink(
            #                         html.I(
            #                             className="bi bi-upload", id="upload-button"
            #                         )
            #                     )
            #                 ),
            #                 dbc.NavItem(
            #                     dbc.NavLink(
            #                         html.I(
            #                             className="bi bi-bootstrap-reboot",
            #                             id="reload-library",
            #                         )
            #                     )
            #                 ),
            #                 dbc.Tooltip(
            #                     "Upload a new book to the lilbrary.",
            #                     target="upload-button",
            #                     placement="bottom",
            #                 ),
            #                 dbc.Tooltip(
            #                     "Re-index the Calibre Library. Necessary if some changes have been performed to the library.",
            #                     target="reload-library",
            #                     placement="bottom",
            #                 ),
            #             ],
            #             navbar=True,
            #         ),
            #         # class_name="me-auto",
            #     ),
            # ],
            # align="center",
            # className="g-0",
        ],
        fluid=True,
    ),
    color="dark",
    dark=True,
)

# navbar = dbc.NavbarSimple(
#     brand="Colibry",
#     children=[
#         dbc.Button(html.I(className="bi bi-upload"), color="primary", className="me-1", id="upload-button"),
#         dbc.Button(html.I(className="bi bi-bootstrap-reboot"), color="primary", id="reload-library"),
#         dbc.Tooltip(
#             "Upload a new book to the lilbrary.",
#             target="upload-button",
#             placement="bottom"
#         ),
#         dbc.Tooltip(
#             "Re-index the Calibre Library. Necessary if some changes have been performed to the library.",
#             target="reload-library",
#             placement="bottom"
#         )
#     ],
#     brand_href="/home",
#     color="primary",
#     dark=True,
# )


app.layout = html.Div([dcc.Store(id="library"), navbar, dash.page_container], className="")


@callback(Output("library", "data"), Input("reload-library", "n_clicks"))
def load_library(_n_clicks):
    calibre_library = CalibreLibrary(APP_CONFIG.library_path)
    books_metadata = calibre_library.list()

    return [e.model_dump_json() for e in books_metadata]


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run(debug=APP_CONFIG.debug)
