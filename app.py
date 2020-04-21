import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True
