import pandas as pd
import polars as pl
import numpy as np
import os
from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output, State
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as plot

import plotly.io as pio
pio.templates.default = "seaborn"


def read_feather(source_file):
    feather_file_list = os.listdir(source_file)
    df = pd.DataFrame()
    for feather_files in feather_file_list:
        if feather_files.endswith(".feather"):
            strfile = source_file + feather_files
            df1 = pd.read_feather(strfile)
            df = pd.concat([df, df1], ignore_index=True, sort=False)
    return df

#data = read_feather("Data/Tonghop/")

#data = df.groupby(['Date','Mã sản phẩm','Tên sản phẩm','Mã siêu thị','Tên ST','RSM tháng 6','AM tháng 6','Miền','Tỉnh/thành','Trạng thái kinh doanh','Nhóm hàng']).sum().reset_index()
df = pl.from_pandas(read_feather("Data/Tonghop/"))
app = JupyterDash(__name__)
product_list = df['Tên sản phẩm'].unique().tolist()
sub_group_list = df['Nhóm hàng'].unique().tolist()
store_list = df['Mã siêu thị'].unique().tolist()
app.layout = html.Div([
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

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('store_selected', 'value'),
    Input('sub_group_selected', 'value'),
    Input('product_selected', 'value'),
    State('store_selected', 'value'))
def update_figure(store_selected,sub_group_selected,product_selected,store_state):

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Số lượng nhập sản phẩm", "Số lượng bán sản phẩm"), horizontal_spacing=0.05)

    if not store_state:
        data_sale = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)],index=['Date'],values='Số lượng bán',aggfunc=np.sum).reset_index()
        data_nhap = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)],index=['Date'],values='Số lượng nhập',aggfunc=np.sum).reset_index()
    else:
        data_sale = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Số lượng bán',aggfunc=np.sum).reset_index()
        data_nhap = pd.pivot_table(df[(df['Nhóm hàng']==sub_group_selected)&(df['Tên sản phẩm']==product_selected)&(df['Mã siêu thị']==store_selected)],index=['Date'],values='Số lượng nhập',aggfunc=np.sum).reset_index()
    if len(data_sale) == 0:
        data_sale = pd.pivot_table(df,index=['Date'],values='Số lượng bán',aggfunc=np.sum).reset_index()
    if len(data_nhap) == 0:
        data_nhap = pd.pivot_table(df,index=['Date'],values='Số lượng nhập',aggfunc=np.sum).reset_index()

    fig.add_trace(go.Scatter(x = data_nhap["Date"], y = data_nhap["Số lượng nhập"], fill='tozeroy',showlegend=False),row=1, col=1)
    fig.add_trace(go.Scatter(x = data_sale["Date"], y = data_sale["Số lượng bán"], fill='tozeroy' ,showlegend=False),row=1, col=2)
    
    fig.update_layout(title='Biểu đồ số lượng bán và số lượng nhập sản phẩm')
  
    return fig

if __name__ == '__main__':
    app.run_server(mode='inline')