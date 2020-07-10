# -*- coding: utf-8 -*-
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from hapi import ISO_ID
from itertools import groupby

mol_name = [el for el, _ in groupby([{'name':ISO_ID[i][5],'id':ISO_ID[i][0]}for i in ISO_ID.keys()])]
mol_name_hitemp = {'H2O':[0,30000],
                   'CO2': [258,9648],
                   'N2O':[0,12899],
                   'CO':[2,22149],
                   'CH4':[0,13400],
                   'NO':[0,26777],
                   'NO2':[0,4775],
                   'OH':[0,19268]
                   }
about =html.Div([
    html.H3(u'О проекте'),
    html.Br(),
    html.Div(u'Выпускная квалификационная работа студента УТб-4301-01-00 Шевченко О. П. \n г.Киров 2020г'),
    html.Div([u'Источники данных',
        html.Div([
            dcc.Link('Hitran', href=' http://www.hitran.org'),
            html.Div(['''R.V. Kochanov, I.E. Gordon, L.S. Rothman, P. Wcislo, C. Hill, J.S. Wilzewski,
                HITRAN Application Programming Interface (HAPI): A comprehensive approach to working with spectroscopic data,
                J. Quant. Spectrosc. Radiat. Transfer 177, 15-30 (2016)''',
                dcc.Link('Hitran HAPI', href=' http://www.hitran.org/hapi'),
                ]),
        ]),
    ]),
    dcc.Link(u'<- Назад ', href='/'),
])


hitran = html.Div([
    html.H4('Hitran'),
    html.Div([
        html.H4([u'Шаг1. Выберете молекулы']),
        dcc.Dropdown(
            id='hitran-molecule-name-dropdown',
            options=[
               dict(label = i['name'], value = i['name']) for i in mol_name
                ],
            value = ['H2O'],
            multi= True,
           # persistence=True
            ),
        ]),
    html.Div([
        html.H4([u'Шаг 2. Выберете изотопы']),
        html.Div(
            id = 'hitran-isotopes-checklists',
            children = [],
            style= {'columnCount': 4}),
        ],style= {'display':'inline-block' }),#'display':'inline-block',
    html.Div([
            html.H4([u'Шаг3. Введите диапазон']),
            dcc.Dropdown(
                id='wavenumber-or-wavelength',
                options=[
                    {'label':u'волнового числа', 'value':'wavenumber'},
                    {'label': u'длинны волны', 'value':'wavelength'},
                    ],
                value = 'wavelength',
                ),
            html.Label([u'Минимум']),
            dcc.Input(
                id={ 'type':'input-wave', 'id':'min'},
                type="number",
                placeholder=u"Введите минимальное ",
                value= 	1000,
                debounce=True
                ),
            html.Label([u'Максимум']),
            dcc.Input(
                id={'type':'input-wave', 'id':'max'},
                type="number",
                placeholder= "Введите максимальное ",
                value = 3000,
                debounce=True
                ),
            ], style= {} ),
    html.Div([
        html.H4([u'Шаг 4. Введите температуру и давление']),
        html.Label([u'Температура в кельвинах']),
        dcc.Input(
            id='input-temperature',
            type="number",
            placeholder=u"Введите температуру",
            value= 296,
            debounce=True
            ),
        html.Label([u'Давление']),
        dcc.Dropdown(
            id='atm-or-Pa',
            options=[
                {'label': u'атмосферы', 'value': 'atm'},
                {'label': u'Паскали', 'value': 'Pa'}
                ],
            value = 'Pa',
            ),
        dcc.Input(
            id='input-pressure',
            type="number",
            placeholder= "Введите давление " ,
            value = 101325,
            debounce=True
            )
        ], style={'display':'inline'}),
    html.Div([
        html.H4(u'Шаг 5. Создание смеси'),
        dcc.Input(
            id='input-name-mixture',
            placeholder= u"Введите название смеси " ,
            value = u'Смесь газов',
            debounce=True
            ),
        html.Div(id = 'input-procent-container'),
        #html.Button(u'Создать смесь' ,id='create-mixture', n_clicks = 0)
    ])
],style= {})

hitemp=html.Div([
    html.H3('Hitemp'),
    html.Div([
        u'В разработке',
    ])
])


geisa=html.Div([
    html.H3('GEISA'),
    html.Div([
        u'В разработке',
    ])
])

from_file=html.Div([
    html.H3(u'Из файла'),
    html.Div([
        u'В разработке',
    ])
])



main =html.Div([
    html.Div([
        dcc.Tabs(id = 'db-choise',value = "HITRAN",children=[
            dcc.Tab(label = "HITRAN", value = "HITRAN",children = [hitran]),
            dcc.Tab(label = "HITEMP", value = "HITEMP", children = [hitemp]),
            dcc.Tab(label = "GEISA", value = "GEISA", children = [geisa]),
            dcc.Tab(label = u"Из файла", value = "file", children = [from_file]),
            ],),
        ], style= {'display': 'grid'}),
    html.Div([
        dcc.Tabs(id = 'output-tab',value = "table",children=[
            dcc.Tab(value = 'table',label = u"Информация об изотопах", children = [
                dash_table.DataTable(
                    id = 'mixture-table',
                    columns=[
                            {'id': 'isotope-name-column', 'name': u'Изотоп'},
                            {'id': 'data-source', 'name': u'Иcточник'},
                            {'id': 'min-wavenumber-column', 'name': u'Минимальное волновое число /\n длинна волны, см^-1 / мкм', 'type': 'numeric'},
                            {'id': 'max-wavenumber-column', 'name': u'Максимальное волновое число /\n длинна волны, см^-1 / мкм', 'type': 'numeric'},
                            ],
                    style_cell={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        }
                    #editable=True,
                    ),
                ]),
            dcc.Tab( value = "graf",label = "График", children = [
                html.Div(id = 'graf-container',children=[]),
                dcc.Graph(id='my-graph'),
                ]),
            ], style = {}),
        ])
    ], style= {'columnCount': 2})