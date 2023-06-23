import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

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
data = df.groupby(['Tên sản phẩm']).agg({"Số lượng":np.sum}).reset_index().sort_values(by="Số lượng",ascending=False).head(10)


st.sidebar.header("Bộ lọc")

Store = st.sidebar.multiselect(
    "Select Store",
    options=data["Tên sản phẩm"].unique(),
    default=data["Tên sản phẩm"].unique()
)

df_selection = data.query("`Tên sản phẩm` == @Store")

pie_chart = px.pie(df_selection, values='Số lượng', names='Tên sản phẩm', title='Top 10 SKU')
#st.plotly_chart(pie_chart)

bar_chart = px.bar(df_selection, x='Tên sản phẩm', y='Số lượng')
#st.plotly_chart(bar_chart)

left_columns, right_columns = st.columns(2)
left_columns.plotly_chart(pie_chart,use_container_width=True)
right_columns.plotly_chart(bar_chart,use_container_width=True)