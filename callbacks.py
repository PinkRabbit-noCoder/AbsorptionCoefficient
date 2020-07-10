# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output, State ,ALL, MATCH
import dash_html_components as html
import dash_core_components as dcc

import uuid
import os

from range_wavenumbers import RANGE_WAVENUMBERS

from hapi import *

from app import app

from itertools import chain


def wavelengthToWavenumber(wavelength):
    if wavelength== 0: return 0
    return 1.0/(wavelength*0.0001)


def wavenumberToWavelength(wavenumber):
    if wavenumber== 0: return 0
    return (1.0/wavenumber)*10000


def atmToPa(atm):
    return atm*101325.0


def paToAtm (pa):
    return pa/101325.0


def getInfoAboutIsotope(iso_name):
    for i in ISO_ID:
        if iso_name in ISO_ID[i]:
            return ISO_ID[i]
    return []


def getDataForGraf(isotopes_checked_lists, min_wavenumber, max_wavenumber, temperature, pressure, nu_or_lam):
    data =[]
    excepion = {}
    for list in isotopes_checked_lists:
        for isotope in list:
            temp = addAbsorptionCoefficient(isotope, min_wavenumber, max_wavenumber, temperature, pressure, nu_or_lam)
            if 'error' not in temp.keys():
                data.append(temp)
            else:
                excepion = temp
    return data, excepion



def addAbsorptionCoefficient(isotope_name, min_wavenumber, max_wavenumber, temperature, pressure, nu_or_lam):
    tables=tableList()
    iso_info=getInfoAboutIsotope(isotope_name)
    nu, coef = 0, 0
    fileName = '{}-{}-{}'.format(iso_info[2],min_wavenumber, max_wavenumber)
    try:
        if fileName not in tables:
            fetch(fileName, iso_info[0], iso_info[1], min_wavenumber, max_wavenumber)
        #print(iso_info[2],min_wavenumber, max_wavenumber, temperature,pressure)
        nu, coef = absorptionCoefficient(SourceTables= fileName ,  Environment = {'p':pressure,'T':temperature})
        if nu_or_lam == 'wavelength':
              lam = [wavenumberToWavelength(i) for i in nu]
              return (dict(x=lam,y=coef, name=isotope_name))
        if nu_or_lam == 'wavenumber':
            return (dict(x=nu,y=coef, name=isotope_name))
    except Exception as e:
        return (dict(error=e, info=iso_info))


@app.callback(Output('hitran-isotopes-checklists', 'children'), [Input('hitran-molecule-name-dropdown', 'value')])
def generate_isotopes_checklist(molecule_name_list):
    checklists = []
    if (molecule_name_list!= []):
        for molecule_name in molecule_name_list:
            iso_list = [ISO_ID[i] for i in ISO_ID if molecule_name in ISO_ID[i]]
            iso_options = []
            for iso in iso_list:
                temp_dict= dict(label = iso[2], value = iso[2])
                iso_options.append(temp_dict)
            new_element = html.Div([
                html.B(molecule_name),
                dcc.Checklist(
                    id={
                        'type': 'hitran-isotopes-checklist',
                        'id': molecule_name
                        },
                    options=iso_options,
                    value=[iso_list[0][2]],
                    persistence_type='session',
                    persistence=molecule_name,
                    style = {'display':'inline-block'}
                    ),
                ], style = {'display':'inline-block'})
            checklists.append(new_element)
    return checklists


@app.callback(
    Output('input-procent-container', 'children'),
    [Input({'type': 'hitran-isotopes-checklist', 'id': ALL}, 'value'),
    Input({'type':'procent', 'id':ALL}, 'value')
    ])
def input_procent(isotopes_checked_lists, inputted_procent):
    inputted_procent = [i if (i!=None) else 0 for i in inputted_procent]
    new_element=[]
    for (i, list) in enumerate(isotopes_checked_lists):
        for (j, isotope) in enumerate(list):
           new_element.append( html.Label(isotope))
           new_element.append(dcc.Input(id={'type':'procent', 'id':isotope}, type= 'number',value = 0, max=(100 - sum(inputted_procent[:i+j])),
              persistence= isotope,
              debounce=True))
    return html.Div(new_element)


'''@app.callback(
    Output('my-graph', 'figure'),
    [Input('create-mixture', 'n_clicks'),],
    [State('input-name-mixture', 'value'),
    State({'type':'procent', 'id':ALL}, 'value'),
    State('my-graph', 'figure')
    ])
def create_mixture(n_clicks,name_mixture, inputted_procent, figure):
    sum_coef=[]
    x = []
    for line in figure[data]:
        sum_coef += line['y']
        x = [i for i in chain(x, line['x'])]
    figure[data].append(dict(name = name_mixture,y= sum_coef, x = x))
    return figure'''


@app.callback(
    Output('mixture-table', 'data'),
    [Input({'type': 'hitran-isotopes-checklist', 'id': ALL}, 'value'),],
    [State('db-choise', 'value')],
    )
def generateMixtureTable(isotopes_checked_lists, data_source):
    data=[]
    for (i, list) in enumerate(isotopes_checked_lists):
        for (j, isotope) in enumerate(list):
           #new_element.append( html.Label(isotope))
           data.append({'isotope-name-column':isotope,'data-source':data_source ,'min-wavenumber-column':'{} / {}'.format(RANGE_WAVENUMBERS[isotope][0],wavenumberToWavelength(RANGE_WAVENUMBERS[isotope][1])),'max-wavenumber-column':'{} / {}'.format(RANGE_WAVENUMBERS[isotope][1],wavenumberToWavelength(RANGE_WAVENUMBERS[isotope][0]))})
    return data


@app.callback(
    [Output('my-graph', 'figure'),
    Output('confirm', 'displayed'),
    Output('confirm', 'message'),],
    [Input ('output-tab','value'),],
    [State({'type': 'hitran-isotopes-checklist', 'id':ALL }, 'value'),
    State({'type': 'input-wave', 'id': 'min'}, 'value'),
    State({'type': 'input-wave', 'id': 'max'}, 'value'),
    State('input-temperature', 'value'),
    State('input-pressure', 'value'),
    State('wavenumber-or-wavelength', 'value'),
    State('atm-or-Pa', 'value'),
    State('input-name-mixture', 'value'),
    State({'type':'procent', 'id':ALL}, 'value')])
def update_graph(tab, isotopes_checked_lists, min_wave, max_wave, temperature, pressure,nu_or_lam, atm_or_pa, name_mixture,inputted_procent):
    if tab == 'graf':
        if nu_or_lam == 'wavelength':
            min_wavenumber = wavelengthToWavenumber(max_wave)
            max_wavenumber = wavelengthToWavenumber(min_wave)
        else:
            min_wavenumber = min_wave
            max_wavenumber = max_wave
        if atm_or_pa =='Pa':
            pressureAtm = paToAtm(pressure)
        else:
            pressureAtm = pressure
        data, excepion = getDataForGraf(isotopes_checked_lists, min_wavenumber, max_wavenumber, temperature, pressureAtm,nu_or_lam)
        sum_coef = []
        x = []
        for index_line,line in enumerate(data):
            '''if len(line['y']) > len(sum_coef):
                for j, c in enumerate(line['y']):
                    if j < len(sum_coef):
                        sum_coef[j] = c*(inputted_procent[i]/100.0)+sum_coef[j]
                    else: sum_coef.append(c*(inputted_procent[i]/100.0))

            if len(sum_coef) > len(line['y']):
                for j, c in enumerate(sum_coef):
                    if j < len(line['y']):
                        sum_coef[j] = c*(inputted_procent[i]/100.0)+sum_coef[j]
                    #else: sum_coef.append(c*(inputted_procent[i]/100.0))'''
            x = sorted( [i for i in chain(x, line['x'])])
            for j, x_i in enumerate(line['x']):
                index = x.index(x_i)
                if sum_coef!=[]:
                    sum_coef.insert(index, line['y'][j]*(inputted_procent[index_line]/100.0))
                else:
                    sum_coef.append(line['y'][j]*(inputted_procent[index_line]/100.0))
        print(len(x), len(sum_coef))
        if any(sum_coef):
            data.insert(0, dict(name = name_mixture,y= sum_coef, x = x))
        xaxis_title = u'Длинна волны, мкм' if nu_or_lam == 'wavelength' else u'Волновое число, см^-1'
        if excepion =={}:
            return {
                'data': data,
                'layout': {
                    'title': u'Коэффициент поглощения различных излучателей \nпри p = {} {}, T = {} K'.format(pressure,atm_or_pa,temperature),
                    'xaxis':{
                        'title':xaxis_title,
                        }
                    }
            }, False, ''
        else:
            return {
                'data': data,
                'layout': {
                    'title': u'Коэффициент поглощения различных излучателей \nпри p = {} {}, T = {} K'.format(pressure,atm_or_pa,temperature),
                    'xaxis':{
                        'title':xaxis_title,
                        }
                    }
            }, True, 'Возникла ошибка \"{}\" при расчете для {}'.format(excepion['error'][0],excepion['info'][2])
    else:
        return {}, False, ''

