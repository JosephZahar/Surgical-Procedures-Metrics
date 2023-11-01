from dash import html, dcc, Dash
from dash.dependencies import Input, Output

# Connect to your src pages
from src.pages import Composition, Distribution, Comparative
import dash_bootstrap_components as dbc

# Connect the navbar to the index
from src.components import navbar
from src.pages.Comparative import comparative_dash
from src.pages.Composition import composition_dash
from src.pages.Distribution import distribution_dash


import pathlib
# Define the navbar
nav = navbar.Navbar()

app = Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=0.7"}],
                external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Define the index page layout
app.layout = html.Div(id='body', className='fullscreen', children=[
    dcc.Location(id='url', refresh=False),
    nav,
    html.Div(id='page-content', children=[]),
])


@app.callback(
    [Output("Composition", "color"),
     Output("Distribution", "color"),
     Output("Comparative", "color")],
    [Input('url', 'pathname')]
)
def update_button_color(pathname):
    if pathname == '/Composition':
        return "light", "outline-secondary", "outline-secondary"
    elif pathname == '/Distribution':
        return "outline-secondary", "light", "outline-secondary"
    elif pathname == '/Comparative':
        return "outline-secondary", "outline-secondary", "light"
    else:
        return "light", "outline-secondary", "outline-secondary"


# Create the callback to handle mutlipage inputs
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Composition':
        return Composition.layout
    if pathname == '/Distribution':
        return Distribution.layout
    if pathname == '/Comparative':
        return Comparative.layout
    else:
        return Composition.layout


@app.callback([Output(component_id="fig1c", component_property="figure"),
               Output(component_id="fig2c", component_property="figure"),
               Output(component_id="fig3c", component_property="figure"),
               Output(component_id="indicators_composition", component_property="figure")],
              [Input(component_id="account_namec", component_property="value"),
               Input(component_id="snomed_codec", component_property="value")])
def callback_function(account_name, procedure_name):
    fig1, fig2, fig3, indicator_composition = composition_dash(account_name, procedure_name)
    return fig1, fig2, fig3, indicator_composition


@app.callback([Output(component_id="fig1d", component_property="figure"),
               Output(component_id="fig2d", component_property="figure"),
               Output(component_id="fig3d", component_property="figure")],
              [Input(component_id="account_named", component_property="value"),
               Input(component_id="snomed_coded", component_property="value")])
def callback_function(account_name, procedure_name):
    fig1, fig2, fig3 = distribution_dash(account_name, procedure_name)
    return fig1, fig2, fig3


@app.callback([Output(component_id="fig1e", component_property="figure"),
               Output(component_id="fig2e", component_property="figure"),
               Output(component_id="fig3e", component_property="figure"),
               Output(component_id="fig4e", component_property="figure"),
               Output(component_id="fig5e", component_property="figure"),
               Output(component_id="fig6e", component_property="figure"),
               Output(component_id="fig7e", component_property="figure"),
               Output(component_id="fig8e", component_property="figure"),
               Output(component_id="indicators_comparative", component_property="figure")],
              [Input(component_id="account_namee", component_property="value"),
               Input(component_id="snomed_codee", component_property="value"),
               Input(component_id="procedure1e", component_property="value"),
               Input(component_id="procedure2e", component_property="value")])
def callback_function(account_name, procedure_name, procedure1, procedure2):
    fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, indicators_comparative = comparative_dash(account_name,
                                                                                              procedure_name,
                                                                                              procedure1, procedure2)
    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, indicators_comparative


# Run the src on localhost:8050
if __name__ == '__main__':
    app.run_server(debug=False)

