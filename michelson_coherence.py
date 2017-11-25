# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 12:52:26 2017

@author: eh94
"""

from bokeh.layouts import layout
from bokeh.models import PanTool, ResetTool, WheelZoomTool, SaveTool, TapTool, ColumnDataSource, Label
from bokeh.models.widgets import DataTable, TableColumn, Button
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models.callbacks import CustomJS
import numpy as np
from scipy import optimize
import pandas as pd

#initialize source data
data=pd.read_csv('data.csv', sep=';')
source = ColumnDataSource(data.to_dict('list'))

#create add_button callback
def add_row():
    new_data={
                'z (mm)': [0.0],
                'contrast': [0.0],
              }
    source.stream(new_data)

#create del_button callback    
def del_row():
    new_data={
                'z (mm)': source.data['z (mm)'][:-1],
                'contrast': source.data['contrast'][:-1]
               }
    source.data=new_data

#create fit function
def fit_data():
    #define the fit function
    def func(x,amp,mean,std):
        return amp*np.exp(-((x-mean)/(2*std))**2)
    
    #get indices of selected data points
    indices=source.selected['1d']['indices']
    
    #get x and y values of selected data points
    z_mm=np.array([source.data['z (mm)'][index] for index in indices])
    contrast=np.array([source.data['contrast'][index] for index in indices])
    
    #fit the selected data points to predefined function
    parameter, variance = optimize.curve_fit(func, z_mm, contrast)
    
    #plot the fit
    fig.line(x=source.data['z (mm)'], y=func(source.data['z (mm)'],*parameter), line_width=3, line_color='firebrick', line_alpha=1)
    
    #illustrate the parameter in textboxes
    amplitude=Label(x=20, y=300, x_units='screen', y_units='screen', text='Amp.: {:.2f}'.format(parameter[0]), text_font_style='bold')
    mean=Label(x=20, y=280, x_units='screen', y_units='screen', text='Mean: {:.2f}'.format(parameter[1]), text_font_style='bold')
    std=Label(x=20, y=260, x_units='screen', y_units='screen', text='Std. Dev.: {:.2f}'.format(parameter[2]), text_font_style='bold')
    fig.add_layout(amplitude)
    fig.add_layout(mean)
    fig.add_layout(std)
    
#create update function
def update():
    return

#create table widget
columns = [
        TableColumn(field="z (mm)", title="z (mm)"),
        TableColumn(field="contrast", title="Contrast"),
    ]
table = DataTable(source=source, columns=columns, editable=True, width=400, height=600)

#create figure
fig = figure(tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool(), TapTool()],output_backend='webgl')
fig.plot_width = 900
fig.plot_height = 600
fig.toolbar.logo = None

#style axis
fig.axis.minor_tick_line_color='black'
fig.axis.minor_tick_in=-6
fig.xaxis.axis_label='z (mm)'
fig.yaxis.axis_label='Contrast'
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
fig.circle(x='z (mm)', y='contrast', size=10, line_color='firebrick', fill_color='firebrick', line_alpha=0.8, fill_alpha=0.3, source=source)
fig.line(x='z (mm)', y='contrast', line_width=2, line_color='gray', line_alpha=0.8, source=source)

#add widgets
add_button = Button(
        label='Add row')
add_button.on_click(add_row)

del_button = Button(
        label='Delete row')
del_button.on_click(del_row)

fit_button = Button(label='Fit data')
fit_button.on_click(fit_data)

export_button = Button(label='Export data', button_type='danger')
js_download = """
var csv = source.get('data');
var filetext = 'z (mm);contrast\\n';
for (i=0; i < csv['contrast'].length; i++) {
    var currRow = [csv['z (mm)'][i].toString(),
                   csv['contrast'][i].toString().concat('\\n')];
    var joined = currRow.join(';');
    filetext = filetext.concat(joined);
}

var filename = 'data.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });
if (navigator.msSaveBlob) { // IE 10+
navigator.msSaveBlob(blob, filename);
} else {
var link = document.createElement("a");
if (link.download !== undefined) { // feature detection
    // Browsers that support HTML5 download attribute
    var url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
}"""
export_button.callback = CustomJS(args=dict(source=source), code=js_download)

#create the layout with figure and widgets
layout=layout([[[fig,fit_button,export_button],[table,del_button,add_button]]])

#stream data
curdoc().add_root(layout)
curdoc().add_periodic_callback(update,500) #updates each 500ms