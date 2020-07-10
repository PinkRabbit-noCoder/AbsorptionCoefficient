# -*- coding: utf-8 -*-
import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'https://codepen.io/chriddyp/pen/brPBPO.css']
app = dash.Dash(__name__, suppress_callback_exceptions=True,external_stylesheets=external_stylesheets )
server = app.server
