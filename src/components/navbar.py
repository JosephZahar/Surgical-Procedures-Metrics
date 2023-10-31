from dash import html
import dash_bootstrap_components as dbc

# Define the navbar structure
def Navbar():
    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.Button("Composition", href="/Composition", id="Composition", color="outline-secondary", className="mr-5")),
                dbc.NavItem(dbc.Button("Distribution", href="/Distribution", id="Distribution", color="outline-secondary", className="mr-5")),
                dbc.NavItem(dbc.Button("Comparative", href="/Comparative", id="Comparative", color="outline-secondary")),
            ],
            brand="Surgical Procedure Metrics",
            brand_href="/Composition",
            id="navbar",
            color="dark",
            dark=True,
        ),
    ])

    return layout


