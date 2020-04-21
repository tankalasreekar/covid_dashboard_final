import dash
import pandas as pd 
import datetime
import plotly.graph_objs as go
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

from apps import stock_market

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

del covid_confirmed, covid_recovered, covid_dead

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