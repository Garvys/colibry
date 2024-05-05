from dash import Dash, html
from calibre.calibre import extract_catalog
import dash_bootstrap_components as dbc
from pathlib import Path

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def display_library(row_size: int = 8):
    calibre_metadata = extract_catalog('/home/garvys/Documents/calibre-dashboard/assets/library')

    rows = [[]]


    for entry in calibre_metadata:

        cover_path = Path(entry.cover).relative_to("/home/garvys/Documents/calibre-dashboard")

        text = entry.title
        if entry.series:
            text += f" - {entry.series}#{entry.series_index}"

        card = dbc.Card(
            [
                dbc.CardImg(src=str(cover_path), top=True),
                dbc.CardBody(
                    [
                        html.H4(entry.title, className="card-title"),
                        html.P(
                            text,
                            className="card-text",
                        ),
                    ]
                ),
            ],
            # style={"width": "18rem"},
        )
        col = dbc.Col(card)

        rows[-1].append(col)

        if len(rows[-1]) == row_size:
            rows.append([])

    rows = [dbc.Row(row) for row in rows if row]

    return rows

navbar = dbc.NavbarSimple(
    # children=[
    #     dbc.NavItem(dbc.NavLink("Page 1", href="#")),
    #     dbc.DropdownMenu(
    #         children=[
    #             dbc.DropdownMenuItem("More pages", header=True),
    #             dbc.DropdownMenuItem("Page 2", href="#"),
    #             dbc.DropdownMenuItem("Page 3", href="#"),
    #         ],
    #         nav=True,
    #         in_navbar=True,
    #         label="More",
    #     ),
    # ],
    brand="Calibre Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)


app.layout = html.Div([
    navbar,
    *display_library()
])

if __name__ == '__main__':
    app.run(debug=True)

