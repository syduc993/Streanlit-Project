import streamlit as st
import pandas as pd
import polars as pl
import numpy as np
import plotly.express as px
import os
from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output, State
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as plot
import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
import plotly.io as pio
pio.templates.default = "plotly"

def read_feather(source_file):
    feather_file_list = os.listdir(source_file)
    df = pd.DataFrame()
    for feather_files in feather_file_list:
        if feather_files.endswith(".feather"):
            strfile = source_file + feather_files
            df1 = pd.read_feather(strfile)
            df = pd.concat([df, df1], ignore_index=True, sort=False)
    return df

df = pl.from_pandas(read_feather("Data/Tonghop/"))
app = JupyterDash(__name__)

product_list = df.select(['Tên sản phẩm']).unique().to_series().to_list()
sub_group_list = df.select(['Nhóm hàng']).unique().to_series().to_list()
store_list = df.select(['Mã siêu thị']).unique().to_series().to_list()
rsm_list = df.select(['RSM']).unique().to_series().to_list()
am_list = df.select(['AM']).unique().to_series().to_list()

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
            sub_group_list,
            sub_group_list[0],
            id='sub_group_selected'
            )],style={'flex': '1.4', 'margin-right': '10px'}),
        html.Div([
            dcc.Dropdown(
            options=product_list,
            value=product_list[0],
            id='product_selected'
            )],style={'flex': '2.4', 'margin-right': '10px'}),
        html.Div([
            dcc.Dropdown(
            options=rsm_list,
            value = rsm_list[0],
            id='rsm_selected'
        )],style={'flex': '2','margin-right': '10px'}),
        html.Div([
            dcc.Dropdown(
            options=am_list,
            value = am_list[0],
            id='am_selected'
        )],style={'flex': '2','margin-right': '10px'}),
        html.Div([
            dcc.Dropdown(
            options=store_list,
            value = store_list[0],
            id='store_selected'
        )],style={'flex': '0.7','margin-right': '10px'}),
        html.Div([
            dcc.Dropdown(
            options=[1,2,3,4,5,6,7,8,9,10,11,12],
            value = datetime.now().month,
            id='month_selected'
        )],style={'flex': '0.7','margin-right': '10px'}),
        html.Div([
            dcc.RangeSlider(
                id = 'days_selected',
                min = 1,
                max = 31,
                step = 1,
                dots = False,
                marks=None,
                tooltip={"placement": "bottom", "always_visible": True},
                value = [1,31],
                allowCross=False,
                )],style={'flex': '1.8'}),
    ], style={'display': 'flex', 'justify-content': 'flex-start', 'align-items': 'center'}),

    dcc.Graph(id='graph-with-slider'),

])

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('sub_group_selected', 'value'),
    Input('product_selected', 'value'),
    Input('rsm_selected', 'value'),
    Input('am_selected', 'value'),
    Input('store_selected', 'value'),
    Input('month_selected', 'value'),
    Input('days_selected', 'value'),
    State('sub_group_selected', 'value'),
    State('product_selected', 'value'),
    State('rsm_selected', 'value'),
    State('am_selected', 'value'),
    State('store_selected', 'value'),
    State('month_selected', 'value'),
    State('days_selected', 'value'),
    )
def update_figure(sub_group_selected,product_selected,rsm_selected,am_selected,store_selected,month_selected,days_selected,sub_group_state,product_state,rsm_state,am_state,store_state,month_state,day_state):

    data = df
    fig = make_subplots(rows=2, cols=2, subplot_titles=("Số lượng nhập sản phẩm", "Số lượng bán sản phẩm","Số lượng tồn sản phẩm","Số lượng hủy sản phẩm"), horizontal_spacing=0.05)
    dict_condition = {}
    if sub_group_state:
        dict_condition['Nhóm hàng'] = sub_group_selected
    if product_state:
        dict_condition['Tên sản phẩm'] = product_selected
    if rsm_state:
        dict_condition['RSM'] = rsm_selected
    if am_state:
        dict_condition['AM'] = am_selected
    if store_state:
        dict_condition['Mã siêu thị'] = store_selected
    for key, values in dict_condition.items():
        data = data.filter((pl.col(key) == values))
    
    if month_state:
        start_date = datetime(2023, month_selected, days_selected[0]).date()
        try:
            end_date = datetime(2023, month_selected, days_selected[1]).date()
        except:
            end_date = first = start_date.replace(day=1) + relativedelta(months=1, days=-1)
        data = data.filter((pl.col('Date') >= start_date) & (pl.col('Date') <= end_date))

    data = data.groupby('Date').agg(pl.col("Số lượng bán","Số lượng nhập","Số lượng thực hủy","Tồn kho siêu thị").sum()).to_pandas().sort_values(by="Date",ascending=True).reset_index().drop(columns=['index'])

    fig.add_trace(go.Scatter(x = data["Date"], y = data["Số lượng nhập"], fill='tozeroy',showlegend=False),row=1, col=1)
    fig.add_trace(go.Scatter(x = data["Date"], y = data["Số lượng bán"], fill='tozeroy' ,showlegend=False),row=1, col=2)
    fig.add_trace(go.Scatter(x = data["Date"], y = data["Tồn kho siêu thị"], fill='tozeroy',showlegend=False),row=2, col=1)
    fig.add_trace(go.Scatter(x = data["Date"], y = data["Số lượng thực hủy"], fill='tozeroy' ,showlegend=False),row=2, col=2)
    
    # fig.update_layout(title= datetime(2023, month_selected, days_selected[0]).date() )

    fig.update_layout(
        xaxis=dict(
            tickformat='%d-%b', # Định dạng lại trục x-axis chỉ hiển thị ngày tháng
        )
    )
 
    return fig

if __name__ == "__main__":
    app.run(debug=False)
