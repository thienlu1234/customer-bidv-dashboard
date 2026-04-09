import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard Khách Hàng")

file = st.file_uploader("Upload file Excel", type=["xlsx"])

# 🔥 Cache để load nhanh
@st.cache_data
def load_data(file):
    return pd.read_excel(file)

if file is not None:
    df = load_data(file)

    st.sidebar.title("Menu")
    option = st.sidebar.radio("Chọn chức năng", [
        "Xem dữ liệu",
        "Top khách hàng"
    ])

    # 📊 INFO DATA (quan trọng)
    st.sidebar.markdown("### 📌 Thông tin data")
    st.sidebar.write(f"Số dòng: {df.shape[0]:,}")
    st.sidebar.write(f"Số cột: {df.shape[1]}")

    # 🔎 Filter nhanh (rất quan trọng)
    search = st.sidebar.text_input("🔍 Tìm theo mã KH")

    if search:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search)).any(axis=1)]

    # =========================
    # 1. XEM DATA
    # =========================
    if option == "Xem dữ liệu":

        st.write("### 📋 Dữ liệu khách hàng")

        # 👉 Cho phép chọn số dòng hiển thị
        num_rows = st.slider("Số dòng hiển thị", 100, 10000, 1000)

        # 👉 Hiển thị data (mượt hơn)
        st.dataframe(
            df.head(num_rows),
            use_container_width=True,
            height=600
        )

        st.info("⚠️ Đang hiển thị một phần dữ liệu để tránh lag")

    # =========================
    # 2. TOP KHÁCH HÀNG
    # =========================
    elif option == "Top khách hàng":

        if "TNT" in df.columns:
            top = df.nlargest(10, "TNT")  # 🔥 nhanh hơn sort
            st.write("### 🏆 Top 10 khách hàng theo TNT")
            st.dataframe(top, use_container_width=True)
        else:
            st.warning("Không tìm thấy cột TNT trong file")
