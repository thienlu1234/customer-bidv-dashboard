import streamlit as st
import pandas as pd

st.title("📊 Dashboard Khách Hàng")

file = st.file_uploader("Upload file Excel", type=["xlsx"])

if file is not None:
    df = pd.read_excel(file)

    st.sidebar.title("Menu")
    option = st.sidebar.radio("Chọn chức năng", [
        "Xem dữ liệu",
        "Top khách hàng"
    ])

    # Xem dữ liệu
    if option == "Xem dữ liệu":
        st.dataframe(df)

    # Top khách hàng
    elif option == "Top khách hàng":
        if "TNT" in df.columns:
            top = df.sort_values(by="TNT", ascending=False).head(10)
            st.write("Top 10 khách hàng theo TNT")
            st.dataframe(top)
        else:
            st.warning("Không tìm thấy cột TNT trong file")
