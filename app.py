import streamlit as st
import pandas as pd

st.title("Dashboard Khách Hàng")

file = st.file_uploader("Upload file Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    st.write("Dữ liệu của bạn:")
    st.dataframe(df)
