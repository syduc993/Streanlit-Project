import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc

import pandas as pd
import polars as pl
import numpy as np
import os
#from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output, State, callback
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as plot

import plotly.io as pio
pio.templates.default = "seaborn"

dash.register_page(__name__, path='/', name='Home') # '/' is home page

def read_feather(source_file):
    feather_file_list = os.listdir(source_file)
    df = pd.DataFrame()
    for feather_files in feather_file_list:
        if feather_files.endswith(".feather"):
            strfile = source_file + feather_files
            df1 = pd.read_feather(strfile)
            df = pd.concat([df, df1], ignore_index=True, sort=False)
    return df

df = read_feather("Data/Tonghop/")

# app = JupyterDash(__name__)
product_list = df['Tên sản phẩm'].unique().tolist()
sub_group_list = df['Nhóm hàng'].unique().tolist()
store_list = df['Mã siêu thị'].unique().tolist()

layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
            sub_group_list,
            sub_group_list[0],
            id='sub_group_selected'
            )],style={'flex': '3', 'margin-right': '10px'}),
        html.Div([
            dcc.Dropdown(
            options=product_list,
            value=product_list[0],
            id='product_selected'
            )],style={'flex': '4', 'margin-right': '10px'}),
        html.Div([
            dcc.Dropdown(
            options=store_list,
            value = store_list[0],
            id='store_selected'
        )],style={'flex': '2'}),
    ], style={'display': 'flex', 'justify-content': 'flex-start', 'align-items': 'center'}),

    dcc.Graph(id='graph-with-slider'),
])

@callback(
    Output('graph-with-slider', 'figure'),
    Input('store_selected', 'value'),
    Input('sub_group_selected', 'value'),
    Input('product_selected', 'value'),
    State('store_selected', 'value'),
    State('product_selected', 'value'),)
def update_figure(store_selected,sub_group_selected,product_selected,store_state,product_state):

    fig = make_subplots(rows=2, cols=2, subplot_titles=("Số lượng nhập sản phẩm", "Số lượng bán sản phẩm","Số lượng tồn sản phẩm","Số lượng hủy sản phẩm"), horizontal_spacing=0.05)

    if not store_state:
        if not product_state:
            data_sale = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)],index=['Date'],values='Số lượng bán',aggfunc=np.sum).reset_index()
            data_nhap = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)],index=['Date'],values='Số lượng nhập',aggfunc=np.sum).reset_index()
            data_stock = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)],index=['Date'],values='Tồn kho siêu thị',aggfunc=np.sum).reset_index()
            data_huy = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)],index=['Date'],values='Số lượng thực hủy',aggfunc=np.sum).reset_index()
        else:
            data_sale = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)],index=['Date'],values='Số lượng bán',aggfunc=np.sum).reset_index()
            data_nhap = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)],index=['Date'],values='Số lượng nhập',aggfunc=np.sum).reset_index()
            data_stock = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)],index=['Date'],values='Tồn kho siêu thị',aggfunc=np.sum).reset_index()
            data_huy = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)],index=['Date'],values='Số lượng thực hủy',aggfunc=np.sum).reset_index()
    else:
        if not product_state:
            data_sale = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Số lượng bán',aggfunc=np.sum).reset_index()
            data_nhap = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Số lượng nhập',aggfunc=np.sum).reset_index()
            data_stock = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Tồn kho siêu thị',aggfunc=np.sum).reset_index()
            data_huy = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Số lượng thực hủy',aggfunc=np.sum).reset_index()
        else:
            data_sale = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Số lượng bán',aggfunc=np.sum).reset_index()
            data_nhap = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Số lượng nhập',aggfunc=np.sum).reset_index()
            data_stock = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Tồn kho siêu thị',aggfunc=np.sum).reset_index()
            data_huy = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Số lượng thực hủy',aggfunc=np.sum).reset_index()
    if len(data_sale) == 0:
        data_sale = pd.pivot_table(df,index=['Date'],values='Số lượng bán',aggfunc=np.sum).reset_index()
    if len(data_nhap) == 0:
        data_nhap = pd.pivot_table(df,index=['Date'],values='Số lượng nhập',aggfunc=np.sum).reset_index()

    fig.add_trace(go.Scatter(x = data_nhap["Date"], y = data_nhap["Số lượng nhập"], fill='tozeroy',showlegend=False),row=1, col=1)
    fig.add_trace(go.Scatter(x = data_sale["Date"], y = data_sale["Số lượng bán"], fill='tozeroy' ,showlegend=False),row=1, col=2)
    fig.add_trace(go.Scatter(x = data_stock["Date"], y = data_stock["Tồn kho siêu thị"], fill='tozeroy',showlegend=False),row=2, col=1)
    fig.add_trace(go.Scatter(x = data_huy["Date"], y = data_huy["Số lượng thực hủy"], fill='tozeroy' ,showlegend=False),row=2, col=2)

    # fig.update_layout(title='Biểu đồ số lượng nhập bán hủy & tồn sản phẩm')
    fig.update_layout(width=1550, height=800)

    return fig