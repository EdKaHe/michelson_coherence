# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 12:52:26 2017

@author: eh94
"""

from bokeh.layouts import layout
from bokeh.models import PanTool, ResetTool, WheelZoomTool, SaveTool, TapTool, ColumnDataSource, Label
from bokeh.models.widgets import DataTable, TableColumn, Button, TextInput
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models.callbacks import CustomJS
import numpy as np
from numpy import exp, log10, log, sin, sinh, sinc, cos, cosh, tan, tanh
from scipy import optimize
import pandas as pd

#initialize source data
filepath='data.xlsx'
filetype=filepath.split('.')[1]
if filetype=='csv':
    data=pd.read_csv(filepath, sep=';')
elif filetype in ['xlsx', 'xslm', 'xls', 'xlsb', 'xlt']:
    data=pd.read_excel(filepath, sep=';')
else:
    print('*.{} is invalid filetype!'.format(filetype))
columns = data.columns
source = ColumnDataSource(data=dict(x=data[columns[0]], y=data[columns[1]]))
table_source=ColumnDataSource(data=data)

#create add_button callback
def add_row():
    new_data=dict(x=[0.0], y=[0.0])
    source.stream(new_data)

#create del_button callback    
def del_row():
    new_data=source.data[:-1]
    source.data=new_data

#create fit function
def fit_data():
    #define the fit function
    func=lambda x,a,b,c,d,e: eval(model_text_input.value)
    
    #get indices of selected data points
    indices=source.selected['1d']['indices']
    indices.sort()
    
    if not indices:
        x=np.array(source.data['x'])
        y=np.array(source.data['y'])
    else:
        #get x and y values of selected data points
        x=np.array([source.data['x'][index] for index in indices])
        y=np.array([source.data['y'][index] for index in indices])
        
    #fit the selected data points to predefined function
    parameter, variance = optimize.curve_fit(func, x, y)

    #plot the fit
    fig.line(x=source.data['x'], y=func(source.data['x'],*parameter), line_width=3, line_color='firebrick', line_alpha=1)
    
    parameter_text_input.value=str(parameter)
    #illustrate the parameter in textboxes
#    amplitude=Label(x=20, y=300, x_units='screen', y_units='screen', text='Amp.: {:.2f}'.format(parameter[0]), text_font_style='bold')
#    mean=Label(x=20, y=280, x_units='screen', y_units='screen', text='Mean: {:.2f}'.format(parameter[1]), text_font_style='bold')
#    std=Label(x=20, y=260, x_units='screen', y_units='screen', text='Std. Dev.: {:.2f}'.format(parameter[2]), text_font_style='bold')
#    fig.add_layout(amplitude)
#    fig.add_layout(mean)
#    fig.add_layout(std)
    
#create update function
def update():
    return

#create table widget
table_columns = [TableColumn(field=column, title=column) for column in columns]
table = DataTable(source=table_source, columns=table_columns, editable=True, width=400, height=600)

#create figure
fig = figure(tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool(), TapTool()],output_backend='webgl')
fig.plot_width = 900
fig.plot_height = 600
fig.toolbar.logo = None

#style axis
fig.axis.minor_tick_line_color='black'
fig.axis.minor_tick_in=-6
fig.xaxis.axis_label=columns[0]
fig.yaxis.axis_label=columns[1]
fig.axis.axis_label_text_color=(0.7,0.7,0.7)
fig.axis.major_label_text_color=(0.7,0.7,0.7)
fig.axis.axis_label_text_font = 'helvetica'
fig.xaxis.axis_label_text_font_size = '16pt'
fig.yaxis.axis_label_text_font_size = '16pt'
fig.axis.axis_label_text_font_style = 'normal'
fig.axis.major_label_text_font = 'helvetica'
fig.axis.major_label_text_font_size = '10pt'
fig.axis.major_label_text_font_style = 'normal'

#plot data
fig.circle(x='x', y='y', size=10, line_color='firebrick', fill_color='firebrick', line_alpha=0.8, fill_alpha=0.3, source=source)
fig.line(x='x', y='y', line_width=2, line_color='gray', line_alpha=0.8, source=source)

#add widgets
add_button = Button(
        label='Add row')
add_button.on_click(add_row)

del_button = Button(
        label='Delete row')
del_button.on_click(del_row)

fit_button = Button(label='Fit data', button_type='danger')
fit_button.on_click(fit_data)

#create text input to enter fit model
model_text_input=TextInput(title='Fit model: ', value='a*exp(-((x-b)/(2*c))**2)')

#create text input to display parameter
parameter_text_input=TextInput(title='Parameter: ', value='')

#create the layout with figure and widgets
layout=layout([[[fig,[model_text_input, parameter_text_input], fit_button],[table,del_button,add_button]]])

#stream data
curdoc().add_root(layout)
curdoc().add_periodic_callback(update,500) #updates each 500ms