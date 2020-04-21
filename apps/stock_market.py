import dash
import datetime
import random
import pandas as pd
import pandas_datareader as pdr
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

from app import app
from apps import country_wise

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

def get_data(inst):    
    data = pd.DataFrame()
    try:
        data = pdr.get_data_yahoo(inst,start,end)
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