import dash
import datetime
import random
import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objs as go
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0][['Symbol','Security']]
company_options = [{'label' : table.iloc[i]['Security'], 'value' : table.iloc[i]['Symbol']} for i in range(table.shape[0])]
OHLC = [{'label' : i, 'value' : i} for i in ['Open','High','Low','Close']]
inst_list = ['^GSPC', 'CL=F','GC=F', 'TLT']
for i,j in zip(inst_list,['S&P 500','Crude Oil','Gold','iShares Barclays 20+ Yr Treas.Bond']):
    company_options.append({'label' : j, 'value' : i})

start = datetime.datetime.strptime("2019-10-17", "%Y-%m-%d")
end = datetime.date.today()
pandemic_declared = datetime.datetime.strptime("2020-3-11", "%Y-%m-%d")
first_case = datetime.datetime.strptime("2019-11-17", "%Y-%m-%d")

covid_confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
covid_recovered = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
covid_dead = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

iso_codes = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv',usecols=['iso3','Country_Region'])
iso_codes.columns = ['iso3','Country/Region']

pandemic_declared = datetime.datetime.strptime("2020-3-11", "%Y-%m-%d")
first_case = datetime.datetime.strptime("2019-11-17", "%Y-%m-%d")
today = datetime.datetime.strptime(covid_confirmed.columns[-1], "%m/%d/%y")
dates_strings = covid_confirmed.columns[4:]

covid_conf_agg = covid_confirmed.groupby('Country/Region').sum().drop(['Lat','Long'],1)
covid_rec_agg = covid_recovered.groupby('Country/Region').sum().drop(['Lat','Long'],1)
covid_dead_agg = covid_dead.groupby('Country/Region').sum().drop(['Lat','Long'],1)

covid_conf_agg.columns = pd.to_datetime(covid_conf_agg.columns)
covid_rec_agg.columns = pd.to_datetime(covid_rec_agg.columns)
covid_dead_agg.columns = pd.to_datetime(covid_dead_agg.columns)

conf_diff = covid_conf_agg.diff(1,1).drop(covid_conf_agg.columns[0],axis=1)
rec_diff = covid_rec_agg.diff(1,1).drop(covid_rec_agg.columns[0],axis=1)
dead_diff = covid_dead_agg.diff(1,1).drop(covid_dead_agg.columns[0],axis=1)

def get_choropleth_data(data):
    dfs = []
    data = data.reset_index()
    data = pd.merge(data,iso_codes,on='Country/Region',how='inner')
    data.drop_duplicates(subset ="Country/Region", keep = 'first', inplace = True)
    for i,j in zip(data['Country/Region'].tolist(),data['iso3'].tolist()):
        temp = pd.DataFrame({'Country' : [],'Date':[],'People':[],'iso3':[]})
        temp['Date'] = pd.to_datetime(data.columns[1:-1].tolist())
        temp['People'] = data[data['Country/Region'] == i].values[0][1:-1].tolist()
        temp['iso3'] = j
        temp['Country'] = i
        temp = temp[temp.Date >= first_case]
        temp.Date = temp.Date.apply(lambda x: x.strftime('%d-%m-%y'))
        dfs.append(temp)
    return pd.concat(dfs,ignore_index=True)

choropleth_animate_conf = get_choropleth_data(covid_conf_agg)
choropleth_animate_rec = get_choropleth_data(covid_rec_agg)
choropleth_animate_dead = get_choropleth_data(covid_dead_agg)

country_indicators = covid_conf_agg.index.unique()
country_options = [{'label' : i, 'value' : i} for i in country_indicators]

dates_axis = covid_conf_agg.columns

trace_1 = go.Scatter(x = dates_axis, y = covid_conf_agg.loc['India'].values,
                    name = 'Confirmed Cases',
                    line = dict(width = 2,
                                color = 'rgb(229, 151, 50)'))
trace_2 = go.Scatter(x = dates_axis, y = covid_rec_agg.loc['India'].values,
                    name = 'Recovered Cases',
                    line = dict(width = 2,
                                color = 'rgb(151, 229, 50)'))
trace_3 = go.Scatter(x = dates_axis, y = covid_dead_agg.loc['India'].values,
                    name = 'Deaths',
                    line = dict(width = 2,
                                color = 'rgb(50, 151, 229)'))
layout = go.Layout(title = 'Overview of affected people in India',
                   hovermode = 'x')

fig = go.Figure(data = [trace_1,trace_2,trace_3], layout = layout)

trace_1 = go.Scatter(x = dates_axis, y = conf_diff.loc['India'].values,
                    name = 'Change in Confirmed Cases',
                    line = dict(width = 2,
                                color = 'rgb(229, 151, 50)'))
trace_2 = go.Scatter(x = dates_axis, y = rec_diff.loc['India'].values,
                    name = 'Change in Recovered Cases',
                    line = dict(width = 2,
                                color = 'rgb(151, 229, 50)'))
trace_3 = go.Scatter(x = dates_axis, y = dead_diff.loc['India'].values,
                    name = 'Change in Deaths',
                    line = dict(width = 2,
                                color = 'rgb(50, 151, 229)'))
layout2 = go.Layout(title = 'Daily change of affected people in India',
                   hovermode = 'x')

fig2 = go.Figure(data = [trace_1,trace_2,trace_3], layout = layout2)

trace_1 = go.Bar(x = dates_axis, y = covid_conf_agg.loc['India'].values,
                    name = 'Confirmed Cases',
                    marker_color = 'orange')
trace_2 = go.Bar(x = dates_axis, y = covid_rec_agg.loc['India'].values,
                    name = 'Recovered Cases',
                    marker_color = 'green')
trace_3 = go.Bar(x = dates_axis, y = covid_dead_agg.loc['India'].values,
                    name = 'Deaths',
                    marker_color = 'red')
layout3 = go.Layout(title = 'Overview of affected people in India',
                   hovermode = 'x',barmode='stack')

fig3 = go.Figure(data = [trace_1,trace_2,trace_3], layout = layout3)

fig_conf = px.choropleth(choropleth_animate_conf,
    locations = 'iso3',color = 'People',hover_name='Country',animation_frame='Date',
    color_continuous_scale = px.colors.sequential.OrRd,range_color=[min(choropleth_animate_conf.People.values),max(choropleth_animate_conf.People.values)],
    )
fig_conf.update_layout(dict(coloraxis = dict(colorbar = dict(thickness = 10,xpad = 0,ypad = 0)),autosize = True))

fig_rec = px.choropleth(choropleth_animate_rec,
    locations = 'iso3',color = 'People',hover_name='Country',animation_frame='Date',
    color_continuous_scale = px.colors.sequential.Greens,range_color=[min(choropleth_animate_rec.People.values),max(choropleth_animate_rec.People.values)])
fig_rec.update_layout(dict(coloraxis = dict(colorbar = dict(thickness = 10,xpad = 0,ypad = 0))))

fig_dead = px.choropleth(choropleth_animate_dead,
    locations = 'iso3',color = 'People',hover_name='Country',animation_frame='Date',
    color_continuous_scale = px.colors.sequential.Greys,range_color=[min(choropleth_animate_dead.People.values),max(choropleth_animate_dead.People.values)])
fig_dead.update_layout(dict(coloraxis = dict(colorbar = dict(thickness = 10,xpad = 0,ypad = 0))))

def make_item(i,group_name,body):
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2([
                    dbc.Button(group_name,
                        id=f"group-{i}-toggle",
                    )
                ],className = 'display-3')
            ),
            dbc.Collapse(
                dbc.CardBody(body),
                id=f"collapse-{i}",
            ),
        ]
    )

accordion_body1 = html.Div([html.P([html.Label("Choose scale"),
                            dcc.Dropdown(id='yaxis_scale',
                                        options=[{'label': i, 'value': i} for i in ['Linear','Logarithmic']],
                                        value='Linear'
                            )],
                        ),
                dcc.Graph(id = 'plot', figure = fig),
    ])

accordion_body2 = html.Div([
                dcc.Graph(id = 'daily-change-plot', figure = fig2),
    ])

accordion_body3 = html.Div([
                dcc.Graph(id = 'bar-plot',figure = fig3 )
    ])


accordion = html.Div(
    [make_item(1,'Overview of Affected People',accordion_body1),
     make_item(2,'Daily Change in Affected People',accordion_body2), 
     make_item(3,'Stacked Overview',accordion_body3)], className="container md-accordion"
)

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

country_wise_layout = html.Div([
            # dropdown
                html.P([
                 html.Label("Choose a country"),
                    dcc.Dropdown(id = 'country_options', options = country_options,
                                value = 'India')
                        ], style = {'width': '400px',
                                    'fontSize' : '15px',
                                    'padding-left' : '10%',
                                    'display': 'inline-block'},className = 'country-dropdown'),
                accordion,
        ],)

world_map_layout = html.Div([html.Div([
                            html.Div([html.H1("COVID Cases by Country as of "+today.strftime("%B")+' '+str(today.day)+'th, '+str(today.year))],
                                style={'textAlign': "center", "padding-bottom": "30"}),]),
                       html.Div([html.Button('Confirmed', id='btn-nclicks-1', n_clicks=0,className='btn btn-outline-warning'),
                        html.Button('Recovered', id='btn-nclicks-2', n_clicks=0,className='btn btn-outline-success'),
                        html.Button('Deaths', id='btn-nclicks-3', n_clicks=0,className='btn btn-outline-primary'),
                        html.Br(),],className='buttons'),
                       dcc.Graph(id = 'choropleth-animate',figure = fig_conf)
                       ], className="container")

stock_market_layout = html.Div([
                            html.Div([
                            html.Div([
                 					html.Label("Choose a company"),
                    				dcc.Dropdown(id = 'company_options', options = company_options,
                                	value = 'GOOG')
                        			], style = {'width': '49%',
                                    'fontSize' : '12px',
                                    'padding-left' : '1%',
                                    'display': 'inline-block'}),
                            html.Div([
                 					html.Label("OHLC"),
                    				dcc.Dropdown(id = 'OHLC', options = OHLC,
                                	value = ['Close'],
                                	multi = True,searchable=False)
                        			], style = {'width': '49%',
                                    'fontSize' : '12px',
                                    'padding-left' : '1%',
                                    'display': 'inline-block'
                                    }),
                            ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),
                        	dcc.Graph(id = 'stock-market-graph'),
                        	dcc.Graph(id = 'ohlc-candlestick'),
                        	dcc.Graph(id = 'returns-graph'),
                        	dcc.Graph(id = 'bollinger-bands'),
                        ], className="container")

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/country_wise':
        return country_wise_layout
    elif pathname == '/apps/stock_market':
        return stock_market_layout
    elif pathname == '/apps/world_map':
        return world_map_layout
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

@app.callback(Output('plot', 'figure'),
             [Input('country_options', 'value'),Input('yaxis_scale', 'value'),])
def update_figure(input1,scale):

    data_conf = covid_conf_agg.loc[input1]
    data_rec = covid_rec_agg.loc[input1]
    data_dead = covid_dead_agg.loc[input1]
    # updating the plot
    trace_1 = go.Scatter(x = data_conf.index, y = data_conf.values,
                        name = 'Confirmed ',
                        line = dict(width = 2,
                                    color = 'rgb(229, 151, 50)'))
    trace_2 = go.Scatter(x = data_rec.index, y = data_rec.values,
                        name = 'Recovered',
                        line = dict(width = 2,
                                    color = 'rgb(151, 229, 50)'))
    trace_3 = go.Scatter(x = data_dead.index, y = data_dead.values,
                        name = 'Dead',
                        line = dict(width = 2,
                                    color = 'rgb(50, 151, 229)'))
    fig = go.Figure(data = [trace_1,trace_2,trace_3], layout = layout)
    fig.update_layout(
    title="Overview of Affected People in "+input1,
    xaxis_title="Date",
    yaxis_title="Number of people",
    height=600,
    yaxis = {'type': 'linear' if scale == 'Linear' else 'log'},
    xaxis={"title":"Date",
                   'rangeselector': {'buttons': list([{'count': 1, 'label': '1M', 
                                                       'step': 'month', 
                                                       'stepmode': 'backward'},
                                                      {'step': 'all'}])},
                   'rangeslider': {'visible': True}, 'type': 'date'},
                   hovermode='x',legend = dict(x=0.3, y=1,itemclick = 'toggleothers'),legend_orientation = 'h',
)
    return fig

@app.callback(Output('daily-change-plot', 'figure'),
             [Input('country_options', 'value')])
def update_figure(input1):
    
    data_conf = conf_diff.loc[input1]
    data_rec = rec_diff.loc[input1]
    data_dead = dead_diff.loc[input1]
    # updating the plot
    trace_1 = go.Scatter(x = data_conf.index, y = data_conf.values,
                        name = 'More Confirmed ',
                        line = dict(width = 2,
                                    color = 'rgb(229, 151, 50)'))
    trace_2 = go.Scatter(x = data_rec.index, y = data_rec.values,
                        name = 'More Recovered',
                        line = dict(width = 2,
                                    color = 'rgb(151, 229, 50)'),)
    trace_3 = go.Scatter(x = data_dead.index, y = data_dead.values,
                        name = 'More Dead',
                        line = dict(width = 2,
                                    color = 'rgb(50, 151, 229)'))
    fig2 = go.Figure(data = [trace_1,trace_2,trace_3], layout = layout2)
    fig2.update_layout(
    title="Daily Change of Affected People in "+input1,
    xaxis_title="Date",
    yaxis_title="Number of people",
    height=600,
    xaxis={"title":"Date",
                   'rangeselector': {'buttons': list([{'count': 1, 'label': '1M', 
                                                       'step': 'month', 
                                                       'stepmode': 'backward'},
                                                      {'step': 'all'}])},
                   'rangeslider': {'visible': True}, 'type': 'date'},
                   hovermode='x',barmode = 'stack',legend = dict(x=0.3, y=0.95,itemclick = 'toggleothers'),legend_orientation = 'h',
)
    return fig2

@app.callback(Output('bar-plot', 'figure'),
             [Input('country_options', 'value')])
def update_figure(input1):
    
    data_conf = covid_conf_agg.loc[input1]
    data_rec = covid_rec_agg.loc[input1]
    data_dead = covid_dead_agg.loc[input1]
    # updating the plot
    trace_1 = go.Bar(x = data_conf.index, y = data_conf.values,
                        name = 'Confirmed ',
                        marker_color = 'orange')
    trace_2 = go.Bar(x = data_rec.index, y = data_rec.values,
                        name = 'Recovered',
                        marker_color = 'green')
    trace_3 = go.Bar(x = data_dead.index, y = data_dead.values,
                        name = 'Dead',
                        marker_color = 'red')
    fig3 = go.Figure(data = [trace_1,trace_2,trace_3], layout = layout3)
    fig3.update_layout(
    title="Overview of Affected People in "+input1,
    xaxis_title="Date",
    yaxis_title="Number of people",
    height=600,
    xaxis={"title":"Date",
                   'rangeselector': {'buttons': list([{'count': 1, 'label': '1M', 
                                                       'step': 'month', 
                                                       'stepmode': 'backward'},
                                                      {'step': 'all'}])},
                   'rangeslider': {'visible': True}, 'type': 'date'},
                   hovermode='x',barmode = 'stack',legend = dict(x=0.3, y=1,itemclick = 'toggleothers'),legend_orientation = 'h',
)
    return fig3

@app.callback(Output('choropleth-animate', 'figure'),
              [Input('btn-nclicks-1', 'n_clicks'),
               Input('btn-nclicks-2', 'n_clicks'),
               Input('btn-nclicks-3', 'n_clicks')])
def displayClick(btn1, btn2, btn3):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        return fig_conf
    elif 'btn-nclicks-2' in changed_id:
        return fig_rec
    elif 'btn-nclicks-3' in changed_id:
        return fig_dead
    else:
        return fig_conf

@app.callback(
    [Output(f"collapse-{i}", "is_open") for i in range(1, 4)],
    [Input(f"group-{i}-toggle", "n_clicks") for i in range(1, 4)],
    [State(f"collapse-{i}", "is_open") for i in range(1, 4)],
)
def toggle_accordion(n1, n2, n3, is_open1, is_open2, is_open3):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "group-1-toggle" and n1:
        return not is_open1, False, False
    elif button_id == "group-2-toggle" and n2:
        return False, not is_open2, False
    elif button_id == "group-3-toggle" and n3:
        return False, False, not is_open3
    return False, False, False

def get_data(inst):    
    data = pd.DataFrame()
    try:
        data = web.DataReader(inst,'yahoo',start,end)
    except Exception as e:
        print('No data available for ',inst, e)

    return data

@app.callback([Output('stock-market-graph', 'figure'),Output('ohlc-candlestick','figure'),
	Output('returns-graph','figure'),Output('bollinger-bands','figure')],
             [Input('company_options', 'value'),Input('OHLC', 'value')])
def update_figure(company,ohlc_selected):

    data = get_data(company)
    pct_change = data['Close'].pct_change().dropna(0)
    rolling_mean = data['Close'].rolling(14).mean()
    rolling_std = data['Close'].rolling(14).std()
    bol_bands = pd.DataFrame()
    bol_bands['Rolling Mean'] = rolling_mean
    bol_bands['Bollinger Upper'] = rolling_mean + (rolling_std * 2)
    bol_bands['Bollinger Lower'] = rolling_mean - (rolling_std * 2)
    bol_bands.index = data.index
    bol_bands.dropna(axis=0)
    traces = []
    bolbands_traces = []

    for option in list(ohlc_selected):
    	if option == 'Low':
    		color = 'red'
    	elif option == 'High':
    		color = '#33CFA5'
    	elif option == 'Close':
    		color = 'orange'
    	else:
    		color = 'blue'

    	traces.append(go.Scatter(x = data.index, y = data[option],
                        name = option,
                        line = dict(width = 1,
                                    color = color)))

    bb_trace1 = go.Scatter(x = bol_bands.index, y = bol_bands['Rolling Mean'],name = 'Rolling(14)',
                        line = dict(width = 2,color = '#ed93ea'))
    bb_trace2 = go.Scatter(x = bol_bands.index, y = bol_bands['Bollinger Upper'],name = 'Bollinger Upper',
                        line = dict(width = 1,color = '#787f82'))
    bb_trace3 = go.Scatter(x = bol_bands.index, y = bol_bands['Bollinger Lower'],name = 'Bollinger Lower',
                        line = dict(width = 1,color = '#787f82'))

    layout = go.Layout(title=company,
    xaxis_title="Date",
    yaxis_title="Price in USD",
    height=600,
    xaxis={"title":"Date",
                   'rangeselector': {'buttons': list([{'count': 1, 'label': '1M', 
                                                       'step': 'month', 
                                                       'stepmode': 'backward'},
                                                      {'step': 'all'}])},
                   'rangeslider': {'visible': True}, 'type': 'date'},
                   hovermode='x',legend = dict(x=0.1, y=1),legend_orientation = 'h',)
    fig = go.Figure(data = traces,layout = layout)
    fig.update_layout({'title':company + ' - OHLC Chart'})

    fig2 = go.Figure(data=go.Candlestick(x=data.index,
                open=data.Open,
                high=data.High,
                low=data.Low,
                close=data.Close),layout = layout)
    fig2.update_layout({'title':company + ' - Candlestick Chart'})

    fig4 = go.Figure(data=[go.Candlestick(x=bol_bands.index,
                open=data.Open,
                high=data.High,
                low=data.Low,
                close=data.Close,name = 'Candlestick',
                increasing = dict( line = dict( color = '#17BECF' ) ),
    decreasing = dict( line = dict( color = '#7F7F7F' ) )),bb_trace3,bb_trace2,bb_trace1],layout = layout)
    fig4.update_layout({'title':company + ' - Bollinger Bands'})


    fig3 = go.Figure(data = [go.Scatter(x=pct_change.index, y=pct_change.values,mode='lines',name='Returns'),
    	go.Scatter(x = [first_case, first_case], y = [min(pct_change)-0.025, max(pct_change)+0.025],
    	 line=dict(color="#dbb446",width=4,dash="dashdot"),name='First Case Registered'),
    	go.Scatter(x = [pandemic_declared, pandemic_declared], y = [min(pct_change)-0.025, max(pct_change)+0.025],
    	 line=dict(color="#fa0519",width=4,dash="dashdot"),name='COVID-19 Declared Pandemic'),
    	],layout = layout)
    fig3.update_layout(yaxis_title="Returns",yaxis = dict(range = [min(pct_change)-0.025, max(pct_change)+0.025]))
    fig3.update_layout({'title':company + ' - Returns'})

    return fig,fig2,fig3,fig4


if __name__ == '__main__':
    app.run_server(debug=True)