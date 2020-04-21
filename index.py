import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

from app import app
from apps import country_wise, stock_market
import dash_bootstrap_components as dbc

apps_bar = dbc.Row(
    [
        dbc.Col(dcc.Link('Home', href='/',className = 'nav-link'),className = 'nav-item'),
        dbc.Col(dcc.Link('Country Wise', href='/apps/country_wise',className = 'nav-link'),className = 'nav-item'),
        dbc.Col(dcc.Link('World Map', href='/apps/world_map',className = 'nav-link'),className = 'nav-item'),
        dbc.Col(dcc.Link('Stock Market', href='/apps/stock_market',className = 'nav-link'),className = 'nav-item'),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src='https://cdn.smassets.net/assets/cms/cc/uploads/sites/7/taller-header-coronavirus-resources.png', height="50px")),
                    dbc.Col(dbc.NavbarBrand("COVID-19 Dashboard", className="navbar-brand")),
                ],
                align="center",
                no_gutters=True,
            ),
        ),
        dbc.NavbarToggler(id="navbar-toggler",className = 'navbar-toggler'),
        dbc.Collapse(apps_bar, id="navbar-collapse", navbar=True),
    ],
    className = 'navbar navbar-expand-lg navbar-dark bg-dark',
)

card1 = dbc.Card(
    [
        dbc.CardImg(src="https://cdn.clipart.email/60e15f1c9ab83ad3c5dd5a97ab95be0a_library-of-pie-chart-icon-clip-art-download-png-files-_751-750.png", top=True),
        dbc.CardBody(
            [
                html.H4("Country Wise Numbers", className="card-title"),
                html.P('Country Wise Overview of Affected People',
                    className="card-text",
                ),
                html.A(dbc.Button("Go to App", color="primary"),id="app1-link",href="/apps/country_wise",)
            ]
        ),
    ],
    style={"width": "18rem"},
    className = 'cards-card inner shadow-sm'
)

card2 = dbc.Card(
    [
        dbc.CardImg(src="/assets/globe2.png", top=True),
        dbc.CardBody(
            [
                html.H4("World Map", className="card-title"),
                html.P([html.Label('Animated World Map'),
                    html.Ul([html.Li('Confirmed'),html.Li('Recovered'),html.Li('Deaths'),]
                        ,style = {'list-style-type': 'none','align-content':'center','padding-right':'35px'})],
                    className="card-text",
                ),
                html.A(dbc.Button("Go to App", color="primary"),id="app2-link",href="/apps/world_map",)
            ]
        ),
    ],
    style={"width": "18rem"},className = 'cards-card inner shadow-sm'
)

card3 = dbc.Card(
    [
        dbc.CardImg(src="https://www.pngmart.com/files/3/Stock-Market-PNG-HD.png", top=True),
        dbc.CardBody(
            [
                html.H4("Stock Market", className="card-title"),
                html.P('Bull Run / Bear Drop',
                    className="card-text",
                ),
                html.A(dbc.Button("Go to App", color="primary"),id="app1-link",href="/apps/stock_market",)
            ]
        ),
    ],
    style={"width": "18rem"},className = 'cards-card inner shadow-sm'
)

cards = dbc.Container([
    dbc.Row([
            html.Div([dbc.Col([
                card1],className = 'cards-column')]),
            html.Div([dbc.Col([
                card2],className = 'cards-column')]),
            html.Div([dbc.Col([
                card3],className = 'cards-column')]),
    ],align = 'stretch',className = 'cards-row',style={'margin': 'auto', 'width': '80vw'})
    ])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),navbar,
    html.Div(id='page-content')
])

index_layout = html.Div([cards])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/country_wise':
        return country_wise.country_wise_layout
    elif pathname == '/apps/stock_market':
        return stock_market.stock_market_layout
    elif pathname == '/apps/world_map':
        return country_wise.world_map_layout
    else:
        return index_layout

@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)