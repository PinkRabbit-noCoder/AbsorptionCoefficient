# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import dash_html_components as html

from app import app
from layouts import main, about
import callbacks

from hapi import db_begin

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
     html.Div(
        className="app-header",
        children=[
            html.Img(src='/assets/logo.png'),
            html.H2([u'ИС моделирования спектров\n коэфициентов   поглощения смеси газов']),
            dcc.Link([

                    html.Img(src='/assets/help.svg'),
                    ], href='/about', className = 'about-link'),
        ],
        style={'background': '#33b5ff'},
    ),
    html.Div(id='page-content'),
    dcc.ConfirmDialog(
        id='confirm',
        ),
],)

db_begin('data')


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
         return main
    elif pathname == '/about':
         return about
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True,  dev_tools_ui=True)

